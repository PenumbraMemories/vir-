# 8021-qq_file_sender.py
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
import win32gui
import win32con
import win32api
import time
import os
import subprocess
import re
import pyperclip
from typing import Dict, List, Optional
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# 添加CORS中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 文件路径处理 ====================

def validate_file_path(file_path: str) -> Optional[str]:
    """验证并规范化文件路径"""
    try:
        file_path = file_path.strip().strip('"').strip("'")
        
        # 如果是绝对路径且存在，直接返回
        abs_path = os.path.abspath(file_path)
        if os.path.exists(abs_path):
            logger.info(f"找到文件: {abs_path}")
            return abs_path
        
        # 常见搜索路径
        common_paths = [
            os.environ.get('USERPROFILE', ''),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Documents'),
            os.getcwd(),
        ]
        
        file_name = os.path.basename(file_path)
        
        for search_path in common_paths:
            if not search_path:
                continue
            candidate = os.path.join(search_path, file_name)
            if os.path.exists(candidate):
                logger.info(f"在 {search_path} 找到文件: {candidate}")
                return candidate
        
        logger.warning(f"找不到文件: {file_path}")
        return None
        
    except Exception as e:
        logger.error(f"验证文件路径时出错: {e}")
        return None


# ==================== 窗口操作 ====================







def find_and_click_search_button() -> bool:
    """打开搜索栏"""
    try:
        logger.warning("使用Ctrl+F快捷键")
        # 使用Ctrl+F
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('F'), 0x21, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('F'), 0x21, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        return True
    except Exception as e:
        logger.error(f"点击搜索按钮失败: {e}")
        return False


def select_friend(friend_name: str) -> bool:
    """在搜索栏中选择QQ好友"""
    try:
        logger.info(f"开始搜索好友: {friend_name}")
        
        
        # 点击搜索按钮或使用快捷键
        find_and_click_search_button()
        time.sleep(0.5)
        
        # 输入好友名称
        pyperclip.copy(friend_name)
        time.sleep(0.2)
        
        # 粘贴好友名称
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('V'), 0x2F, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('V'), 0x2F, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)
        
        # 按下回车键选择好友
        win32api.keybd_event(win32con.VK_RETURN, 0x1C, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_RETURN, 0x1C, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1.0)
        
        logger.info(f"成功选择好友: {friend_name}")
        return True
        
    except Exception as e:
        logger.error(f"选择好友失败: {e}")
        return False


# ==================== 文件发送功能 ====================

def copy_file_to_clipboard(file_path: str) -> bool:
    """复制文件到剪贴板"""
    try:
        logger.info(f"正在复制文件到剪贴板: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return False
        
        # 使用 PowerShell 复制文件到剪贴板
        ps_script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        $fileList = New-Object System.Collections.Specialized.StringCollection
        $fileList.Add("{file_path}")
        [System.Windows.Forms.Clipboard]::SetFileDropList($fileList)
        '''
        
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("文件已复制到剪贴板")
            return True
        else:
            logger.error(f"PowerShell 复制失败: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"复制文件失败: {e}")
        return False


def paste_file_to_chat() -> bool:
    """在当前激活的聊天窗口中粘贴文件（只使用键盘操作）"""
    try:
        # 确保窗口焦点
        time.sleep(0.2)
        
        # 粘贴文件 (Ctrl+V)
        logger.info("执行粘贴操作...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(ord('V'), 0x2F, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(ord('V'), 0x2F, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1.0)
        
        # 发送文件 (回车)
        logger.info("执行发送操作...")
        win32api.keybd_event(win32con.VK_RETURN, 0x1C, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_RETURN, 0x1C, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1.0)
        
        logger.info("文件粘贴并发送成功")
        return True
        
    except Exception as e:
        logger.error(f"粘贴发送文件失败: {e}")
        return False


def send_qq_file(file_path: str, friend_name: Optional[str] = None) -> Dict:
    """发送QQ文件
    
    Args:
        file_path: 文件路径
        friend_name: 好友名称（如果提供，会先选择好友）
    
    Returns:
        操作结果字典
    """
    logger.info(f"开始发送文件: {file_path}, 目标好友: {friend_name if friend_name else '当前窗口'}")
    
    # 验证文件路径
    validated_path = validate_file_path(file_path)
    if not validated_path:
        return {
            "success": False,
            "message": f"文件路径无效: {file_path}",
            "file": None,
            "friend": friend_name
        }
    
    try:
        # 如果需要选择好友
        if friend_name:
            if not select_friend(friend_name):
                return {
                    "success": False,
                    "message": f"选择好友失败: {friend_name}",
                    "file": validated_path,
                    "friend": friend_name
                }
            time.sleep(0.5)
        
        # 复制文件到剪贴板
        if not copy_file_to_clipboard(validated_path):
            return {
                "success": False,
                "message": "复制文件到剪贴板失败",
                "file": validated_path,
                "friend": friend_name
            }
        
        time.sleep(0.3)
        
        # 粘贴并发送文件
        if not paste_file_to_chat():
            return {
                "success": False,
                "message": "粘贴发送文件失败",
                "file": validated_path,
                "friend": friend_name
            }
        
        logger.info(f"文件发送成功: {validated_path}")
        return {
            "success": True,
            "message": f"文件发送成功: {os.path.basename(validated_path)}",
            "file": validated_path,
            "friend": friend_name
        }
        
    except Exception as e:
        logger.error(f"发送文件失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"发送文件失败: {str(e)}",
            "file": validated_path,
            "friend": friend_name
        }


# ==================== 指令解析 ====================

def parse_selectfriend_sendfile_action(message: str) -> Dict:
    """解析消息中的 [ACTION:SELECTFRIEND_SENDFILE] 指令
    
    支持的格式：
    [ACTION:SELECTFRIEND_SENDFILE]好友名称|文件路径
    
    示例：
    [ACTION:SELECTFRIEND_SENDFILE]张三|C:\\Users\\file.pdf
    """
    try:
        # 匹配指令格式 - 修正正则表达式
        pattern = r'\[ACTION:SELECTFRIEND_SENDFILE\](.*?)(?=\[ACTION|$)'
        match = re.search(pattern, message, re.DOTALL)
        
        if not match:
            return {
                "has_action": False,
                "friend_name": None,
                "file_path": None
            }
        
        content = match.group(1).strip()
        logger.info(f"解析指令内容: {content}")
        
        # 使用竖线分隔好友名称和文件路径
        if '|' in content:
            parts = content.split('|', 1)
            friend_name = parts[0].strip()
            file_path = parts[1].strip()
        # 支持中文竖线
        elif '｜' in content:  # 全角竖线
            parts = content.split('｜', 1)
            friend_name = parts[0].strip()
            file_path = parts[1].strip()
        # 支持分号分隔
        elif '；' in content:
            parts = content.split('；', 1)
            friend_name = parts[0].strip()
            file_path = parts[1].strip()
        elif ';' in content:
            parts = content.split(';', 1)
            friend_name = parts[0].strip()
            file_path = parts[1].strip()
        else:
            # 尝试智能解析：如果没有分隔符，可能整个内容就是文件路径
            # 检查是否像文件路径
            if any(ext in content.lower() for ext in ['.pdf', '.jpg', '.png', '.doc', '.xls', '.txt', '.zip', '.rar']):
                logger.warning(f"未找到分隔符，将内容视为文件路径: {content}")
                return {
                    "has_action": True,
                    "friend_name": None,  # 没有指定好友，使用当前窗口
                    "file_path": content,
                    "warning": "未找到分隔符，将整个内容作为文件路径处理"
                }
            else:
                logger.warning(f"无法解析指令内容，缺少分隔符: {content}")
                return {
                    "has_action": True,
                    "friend_name": None,
                    "file_path": None,
                    "parse_error": "格式错误，正确格式: 好友名称|文件路径"
                }
        
        # 验证文件路径不为空
        if not file_path:
            return {
                "has_action": True,
                "friend_name": friend_name,
                "file_path": None,
                "parse_error": "文件路径不能为空"
            }
        
        logger.info(f"解析成功 - 好友: {friend_name if friend_name else '未指定'}, 文件: {file_path}")
        return {
            "has_action": True,
            "friend_name": friend_name if friend_name else None,
            "file_path": file_path
        }
        
    except Exception as e:
        logger.error(f"解析指令失败: {e}")
        return {
            "has_action": False,
            "friend_name": None,
            "file_path": None,
            "parse_error": str(e)
        }


# ==================== 执行指令 ====================

def execute_selectfriend_sendfile(friend_name: str, file_path: str) -> Dict:
    """执行选择好友并发送文件的完整操作"""
    results = []
    
    # 步骤1: 选择好友（如果提供了好友名称）
    if friend_name:
        logger.info(f"步骤1: 选择好友 '{friend_name}'")
        select_success = select_friend(friend_name)
        results.append({
            "step": 1,
            "action": "SELECTFRIEND",
            "success": select_success,
            "message": f"选择好友: {friend_name}"
        })
        
        if not select_success:
            return {
                "success": False,
                "message": f"选择好友失败: {friend_name}",
                "results": results,
                "friend_name": friend_name,
                "file_path": file_path
            }
        time.sleep(0.5)
    else:
        logger.info("未指定好友名称，将使用当前激活的聊天窗口")
        results.append({
            "step": 1,
            "action": "SKIP_SELECTFRIEND",
            "success": True,
            "message": "使用当前激活的聊天窗口"
        })
    
    # 步骤2: 发送文件
    logger.info(f"步骤2: 发送文件 '{file_path}'")
    send_result = send_qq_file(file_path, friend_name=None)  # 已经选择好友，不再重复选择
    results.append({
        "step": 2,
        "action": "SENDFILE",
        "success": send_result["success"],
        "message": send_result["message"]
    })
    
    return {
        "success": send_result["success"],
        "message": "文件发送完成" if send_result["success"] else "文件发送失败",
        "friend_name": friend_name,
        "file_path": file_path,
        "results": results
    }


# ==================== API 接口 ====================

@app.post("/send_qq_file")
async def send_qq_file_endpoint(payload: dict = Body(...)):
    """
    发送QQ文件接口
    
    参数格式:
    {
        "message": "[ACTION:SELECTFRIEND_SENDFILE]好友名称|文件路径",
        "friend_name": "可选，直接指定好友名称",
        "file_path": "可选，直接指定文件路径"
    }
    
    指令格式示例:
    [ACTION:SELECTFRIEND_SENDFILE]张三|C:\\Users\\document.pdf
    """
    try:
        message = payload.get("message", "")
        direct_friend_name = payload.get("friend_name")
        direct_file_path = payload.get("file_path")
        
        logger.info(f"收到发送文件请求")
        logger.debug(f"消息内容: {message[:200] if message else '无'}")
        
        # 优先使用直接提供的参数
        if direct_friend_name is not None and direct_file_path:
            logger.info(f"使用直接参数: 好友={direct_friend_name}, 文件={direct_file_path}")
            result = send_qq_file(direct_file_path, direct_friend_name)
            return result
        
        # 从消息中解析指令
        if message:
            parsed = parse_selectfriend_sendfile_action(message)
            
            if parsed.get("has_action"):
                friend_name = parsed.get("friend_name")
                file_path = parsed.get("file_path")
                
                # 检查解析错误
                if parsed.get("parse_error"):
                    return {
                        "success": False,
                        "message": f"指令解析失败: {parsed['parse_error']}",
                        "format_hint": "正确格式: [ACTION:SELECTFRIEND_SENDFILE]好友名称|文件路径"
                    }
                
                if not file_path:
                    return {
                        "success": False,
                        "message": "未找到文件路径",
                        "error": parsed.get("parse_error", "文件路径为空"),
                        "format_hint": "正确格式: [ACTION:SELECTFRIEND_SENDFILE]好友名称|文件路径"
                    }
                
                logger.info(f"执行指令: 好友={friend_name}, 文件={file_path}")
                
                # 执行完整操作流程
                result = execute_selectfriend_sendfile(friend_name, file_path)
                return result
            else:
                return {
                    "success": False,
                    "message": "消息中不包含有效的 [ACTION:SELECTFRIEND_SENDFILE] 指令",
                    "format_hint": "正确格式: [ACTION:SELECTFRIEND_SENDFILE]好友名称|文件路径",
                    "example": "[ACTION:SELECTFRIEND_SENDFILE]张三|C:\\\\Users\\\\document.pdf"
                }
        
        return {
            "success": False,
            "message": "未提供有效参数",
            "usage": {
                "direct_params": "提供 friend_name 和 file_path 参数",
                "message_format": "消息中包含 [ACTION:SELECTFRIEND_SENDFILE]好友名称|文件路径",
                "example": {
                    "message": "[ACTION:SELECTFRIEND_SENDFILE]张三|C:\\\\file.pdf"
                }
            }
        }
        
    except Exception as e:
        logger.error(f"发送文件请求失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"处理失败: {str(e)}"
        }


@app.post("/select_friend")
async def select_friend_endpoint(payload: dict = Body(...)):
    """选择QQ好友接口"""
    try:
        friend_name = payload.get("friend_name")
        message = payload.get("message", "")
        
        if not friend_name and message:
            # 尝试从消息中解析
            parsed = parse_selectfriend_sendfile_action(message)
            friend_name = parsed.get("friend_name")
        
        if not friend_name:
            return {
                "success": False,
                "message": "未提供好友名称"
            }
        
        logger.info(f"选择好友: {friend_name}")
        result = select_friend(friend_name)
        
        return {
            "success": result,
            "message": f"选择好友{'成功' if result else '失败'}: {friend_name}",
            "friend_name": friend_name
        }
        
    except Exception as e:
        logger.error(f"选择好友请求失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"处理失败: {str(e)}"
        }


@app.post("/send_file_current")
async def send_file_to_current_chat(payload: dict = Body(...)):
    """向当前聊天窗口发送文件接口"""
    try:
        file_path = payload.get("file_path")
        
        if not file_path:
            return {
                "success": False,
                "message": "未提供文件路径"
            }
        
        logger.info(f"向当前窗口发送文件: {file_path}")
        result = send_qq_file(file_path, friend_name=None)
        return result
        
    except Exception as e:
        logger.error(f"发送文件请求失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"处理失败: {str(e)}"
        }








# ==================== 主函数 ====================

if __name__ == "__main__":
    import uvicorn
    
    
    print("QQ文件发送服务 (端口: 8021)")
    
    
    # 检查依赖
    try:
        import win32con, win32api, pyperclip
        print("✓ 依赖检查通过")
    except ImportError as e:
        print(f"\\n✗ 缺少依赖: {e}")
        print("请安装: pip install pywin32 pyperclip uvicorn fastapi")
        input("按回车键退出...")
        exit(1)
    
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8025)