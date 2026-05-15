# 8008-检测opencmd指令并执行
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
import subprocess
import re
import time
import tempfile
import os
from typing import Dict, List, Union

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _split_commands(command: str) -> List[str]:
    """智能拆分命令（处理 && 和 | 连接的多个命令）"""
    # 注意：不拆分解释器内部的 &&（比如 python -c "cmd1 && cmd2"）
    commands = []
    current = []
    in_string = False
    quote_char = None
    i = 0
    
    while i < len(command):
        char = command[i]
        
        # 处理字符串开始/结束
        if char in ('"', "'") and (i == 0 or command[i-1] != '\\'):
            if not in_string:
                in_string = True
                quote_char = char
            elif char == quote_char:
                in_string = False
                quote_char = None
        
        # 不在字符串内，且遇到 && 或 ||
        if not in_string and i < len(command) - 1:
            if command[i:i+2] == '&&':
                # 找到分隔符，保存当前命令
                commands.append(''.join(current).strip())
                current = []
                i += 2
                continue
            elif command[i:i+2] == '||':
                commands.append(''.join(current).strip())
                current = []
                i += 2
                continue
        
        current.append(char)
        i += 1
    
    if current:
        commands.append(''.join(current).strip())
    
    return commands if len(commands) > 1 else [command]

def _execute_python_code_via_tempfile(code: str, timeout: int = 60) -> Dict:
    """通过临时文件执行Python代码"""
    temp_file = None
    
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', 
                                        delete=False, encoding='utf-8') as f:
            # 添加编码声明和错误处理
            f.write('# -*- coding: utf-8 -*-\n')
            f.write('import sys\n')
            f.write('import traceback\n\n')
            f.write('try:\n')
            # 缩进原来的代码
            for line in code.split('\n'):
                f.write(f'    {line}\n')
            f.write('except Exception as e:\n')
            f.write('    print(f"Error: {e}", file=sys.stderr)\n')
            f.write('    traceback.print_exc()\n')
            f.write('    sys.exit(1)\n')
            
            temp_file = f.name
        
        logger.info(f"创建临时Python文件: {temp_file}")
        
        # 执行临时文件
        start_time = time.time()
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            logger.info(f"✓ 临时文件Python命令执行成功 (耗时: {execution_time:.3f}秒)")
            if result.stdout:
                logger.debug(f"输出: {result.stdout[:200]}")
        else:
            logger.error(f"✗ 临时文件Python命令执行失败 (返回码: {result.returncode})")
            if result.stderr:
                logger.error(f"错误输出: {result.stderr[:500]}")
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": execution_time
        }
        
    except subprocess.TimeoutExpired:
        logger.error(f"临时文件Python命令执行超时 ({timeout}秒)")
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"命令执行超时（{timeout}秒）",
            "execution_time": timeout
        }
    except Exception as e:
        logger.error(f"临时文件Python命令执行异常: {str(e)}")
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "execution_time": 0
        }
    finally:
        # 清理临时文件
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
                logger.debug(f"已删除临时文件: {temp_file}")
            except Exception as e:
                logger.warning(f"删除临时文件失败: {str(e)}")

def _execute_single_command(command: str) -> Dict:
    """执行单条命令 - 增强对复杂Python命令的支持"""
    start_time = time.time()
    
    try:
        logger.info(f"执行子命令: {command[:150]}...")
        
        # 自动修复pip命令中的无效参数
        command = command.replace('--format=table', '--format=columns')
        
        # 检查是否是PowerShell命令，移除可能导致挂起的参数
        if command.strip().lower().startswith("powershell"):
            command = command.replace("-NoExit", "")
        
        # Python命令特殊处理 - 使用临时文件执行复杂命令
        if command.strip().startswith("python -c") or command.strip().startswith("python.exe -c"):
            # 提取 -c 后面的代码
            # 匹配 python -c "code" 或 python -c 'code'
            match = re.search(r'python(?:\.exe)?\s+-c\s+["\'](.+)["\']$', command, re.DOTALL)
            
            if match:
                python_code = match.group(1)
                
                # 检查代码复杂度（包含字典、列表、多行等）
                is_complex = any([
                    '{' in python_code and '}' in python_code,  # 字典
                    '[' in python_code and ']' in python_code,  # 列表
                    '\n' in python_code,  # 多行
                    'for ' in python_code,
                    'if ' in python_code,
                    'def ' in python_code,
                    'class ' in python_code,
                    len(python_code) > 300  # 代码太长也使用文件
                ])
                
                if is_complex:
                    logger.info("检测到复杂Python代码，使用临时文件执行")
                    return _execute_python_code_via_tempfile(python_code, timeout=60)
                else:
                    logger.info("执行简单Python -c 命令（直接执行）")
                    
                    # 直接执行简单命令
                    result = subprocess.run(
                        command, 
                        shell=True, 
                        capture_output=True, 
                        text=True, 
                        encoding='gbk',
                        errors='replace', 
                        timeout=60
                    )
                    
                    execution_time = time.time() - start_time
                    
                    if result.returncode == 0:
                        logger.info(f"✓ Python命令执行成功 (耗时: {execution_time:.3f}秒)")
                        if result.stdout:
                            logger.debug(f"输出: {result.stdout[:200]}")
                    else:
                        logger.error(f"✗ Python命令执行失败 (返回码: {result.returncode})")
                        if result.stderr:
                            logger.error(f"错误输出: {result.stderr[:500]}")
                    
                    return {
                        "success": result.returncode == 0,
                        "returncode": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "execution_time": execution_time
                    }
            else:
                # 如果无法提取代码，尝试直接执行
                logger.warning("无法提取Python代码，尝试直接执行")
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    encoding='gbk',
                    errors='replace', 
                    timeout=60
                )
                
                execution_time = time.time() - start_time
                
                return {
                    "success": result.returncode == 0,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "execution_time": execution_time
                }
        
        # 执行普通命令
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='gbk',
            errors='replace', 
            timeout=30
        )
        
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            logger.info(f"✓ 子命令执行成功 (耗时: {execution_time:.3f}秒)")
        else:
            logger.error(f"✗ 子命令执行失败 (返回码: {result.returncode})")
            if result.stderr:
                logger.error(f"错误输出: {result.stderr[:500]}")
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": execution_time
        }
        
    except subprocess.TimeoutExpired:
        logger.error(f"子命令执行超时 (60秒)")
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": "命令执行超时（60秒）",
            "execution_time": 60
        }
    except Exception as e:
        logger.error(f"子命令执行异常: {str(e)}")
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "execution_time": 0
        }

def _execute_command(command: str) -> Dict:
    """执行终端命令并捕获输出（支持复杂的多命令）"""
    start_time = time.time()
    
    logger.info(f"========== 命令执行开始 ==========")
    logger.info(f"原始命令: {command[:200]}...")
    logger.info(f"命令长度: {len(command)} 字符")
    logger.info(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    
    # 对于包含复杂语法的 Python 命令，只做日志记录，不阻止执行
    if "python -c" in command:
        if 'for' in command or 'if' in command or 'with' in command or 'f"' in command or "f'" in command:
            logger.info("检测到包含复杂语法的Python命令，将直接执行（由Python解释器处理语法）")
    
    # 拆分命令（如果是复合命令）
    sub_commands = _split_commands(command)
    
    if len(sub_commands) > 1:
        logger.info(f"检测到复合命令，拆分为 {len(sub_commands)} 个子命令")
        results = []
        all_success = True
        
        for i, sub_cmd in enumerate(sub_commands, 1):
            logger.info(f"--- 执行子命令 {i}/{len(sub_commands)} ---")
            result = _execute_single_command(sub_cmd)
            results.append(result)
            
            # 如果命令失败且不是使用 || 连接的，停止执行
            if not result["success"] and "||" not in command:
                all_success = False
                logger.error(f"子命令 {i} 执行失败，停止执行后续命令")
                break
        
        execution_time = time.time() - start_time
        
        # 汇总结果
        combined_stdout = "\n".join([r["stdout"] for r in results if r["stdout"]])
        combined_stderr = "\n".join([r["stderr"] for r in results if r["stderr"] if r["stderr"]])
        
        logger.info(f"========== 命令执行结束 ==========")
        logger.info(f"总耗时: {execution_time:.3f}秒")
        
        return {
            "success": all_success,
            "returncode": 0 if all_success else -1,
            "stdout": combined_stdout,
            "stderr": combined_stderr,
            "execution_time": execution_time,
            "sub_commands_count": len(sub_commands)
        }
    else:
        # 单条命令直接执行
        result = _execute_single_command(command)
        
        execution_time = time.time() - start_time
        
        if result["success"]:
            logger.info(f"✓ 命令执行成功")
            logger.info(f"返回码: {result['returncode']}")
            logger.info(f"执行耗时: {execution_time:.3f}秒")
        else:
            logger.error(f"✗ 命令执行失败")
            logger.error(f"返回码: {result['returncode']}")
            logger.error(f"执行耗时: {execution_time:.3f}秒")
        
        logger.info(f"========== 命令执行结束 ==========")
        
        return {
            "success": result["success"],
            "returncode": result["returncode"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "execution_time": execution_time
        }

def _parse_actions(message: str) -> Dict:
    """解析AI回复中的操作标记 - 支持命令中包含中括号，支持多条命令"""
    actions = {}
    commands = []
    
    # 查找所有 [ACTION:OPENCMD] 的位置
    search_start = 0
    marker = '[ACTION:OPENCMD]'
    marker_len = len(marker)
    
    while True:
        marker_pos = message.find(marker, search_start)
        if marker_pos == -1:
            break
        
        # 找到标记的开始位置
        cmd_start = marker_pos + marker_len
        
        # 查找下一个 [ACTION: 的位置（作为结束标记）
        next_action_pos = message.find('[ACTION:', cmd_start)
        
        if next_action_pos == -1:
            # 没有下一个ACTION，取到字符串末尾
            command = message[cmd_start:].strip()
        else:
            # 有下一个ACTION，取到它之前
            command = message[cmd_start:next_action_pos].strip()
        
        if command:
            commands.append(command)
            logger.info(f"提取到OPENCMD命令 #{len(commands)}，长度: {len(command)} 字符")
            logger.debug(f"命令内容前100字符: {command[:100]}...")
        
        # 更新搜索位置，继续查找下一个标记
        search_start = marker_pos + marker_len
    
    # 为了保持向后兼容，如果有多个命令，用列表存储
    if commands:
        if len(commands) == 1:
            actions["OPENCMD"] = commands[0]
        else:
            actions["OPENCMD"] = commands  # 多个命令时返回列表
            logger.info(f"共提取到 {len(commands)} 条命令")
    else:
        actions["OPENCMD"] = None
    
    return actions

def _handle_opencmd(command: str) -> Dict:
    """处理OPENCMD命令"""
    result = _execute_command(command)
    return {
        "action": "execute_command",
        "success": result.get("success", False),
        "message": "命令执行成功" if result.get("success") else "命令执行失败",
        "details": {
            "command": command[:200] + "..." if len(command) > 200 else command,
            "stdout": result.get("stdout"),
            "stderr": result.get("stderr"),
            "returncode": result.get("returncode"),
            "execution_time": result.get("execution_time")
        }
    }

def process_ai_message(message: str) -> Dict:
    """处理AI消息，根据标记调用相应的服务 - 支持多条OPENCMD命令"""
    actions = _parse_actions(message)
    results = []

    opencmd_commands = actions["OPENCMD"]
    
    if opencmd_commands:
        # 判断是单条命令还是多条命令
        if isinstance(opencmd_commands, list):
            logger.info(f"检测到 {len(opencmd_commands)} 条OPENCMD命令")
            for idx, cmd in enumerate(opencmd_commands, 1):
                logger.info(f"执行命令 {idx}/{len(opencmd_commands)}")
                results.append(_handle_opencmd(cmd))
            
            # 检查是否有任何命令失败
            all_success = all(r["success"] for r in results)
            return {
                "success": all_success,
                "message": f"共执行 {len(results)} 条命令，{'全部成功' if all_success else '存在失败命令'}",
                "results": results
            }
        else:
            # 单条命令（向后兼容）
            logger.info(f"检测到OPENCMD命令")
            results.append(_handle_opencmd(opencmd_commands))
            return {
                "success": results[0]["success"],
                "message": "OPENCMD命令处理完成",
                "results": results
            }
    
    # 如果没有检测到OPENCMD操作
    return {
        "success": True,
        "message": "未检测到OPENCMD操作，消息将传递给其他服务处理",
        "results": []
    }


@app.post("/process_ai_message")
async def process_ai_message_endpoint(payload: dict = Body(...)):
    """
    处理AI消息，只处理OPENCMD（终端命令执行）
    """
    try:
        message = payload.get("message", "")
        if not message:
            return {
                "success": False,
                "message": "未提供消息内容",
                "results": []
            }

        result = process_ai_message(message)
        return result

    except Exception as e:
        logger.error(f"处理AI消息时发生错误: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"处理失败: {str(e)}",
            "results": []
        }

if __name__ == "__main__":
    import uvicorn
    logger.info("[OPENCMD]服务已启动在8008端口...")
    uvicorn.run(app, host="0.0.0.0", port=8008)