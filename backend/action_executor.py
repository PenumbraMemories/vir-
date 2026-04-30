#[ACTION:OPENCMD]
#8008
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
import subprocess
import re
import sys
import os
from typing import Dict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
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

# 添加backend目录到Python路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

def _execute_command(command: str) -> Dict:
    """执行终端命令并捕获输出"""
    try:
        logger.info(f"执行命令: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        logger.error(f"执行命令失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e)
        }

def _parse_actions(message: str) -> Dict:
    """解析AI回复中的操作标记"""
    actions = {}
    for action in ["OPENCMD", "TOPWINDOWS"]:
        pattern = rf'\[ACTION:{action}\](.*?)(?=\[ACTION|$)'
        matches = re.findall(pattern, message)
        actions[action] = matches[0].strip() if matches else None
    return actions

def _handle_opencmd(command: str) -> Dict:
    """处理OPENCMD命令"""
    result = _execute_command(command)
    return {
        "action": "execute_command",
        "success": result.get("success", False),
        "message": "命令执行成功" if result.get("success") else "命令执行失败",
        "details": {
            "command": command,
            "stdout": result.get("stdout"),
            "stderr": result.get("stderr"),
            "returncode": result.get("returncode")
        }
    }

def _handle_topwindows(window_title: str) -> Dict:
    """处理TOPWINDOWS命令"""
    from windows_service import set_window_topmost
    result = set_window_topmost(window_title)
    return {
        "action": "set_window_topmost",
        "success": result.get("success", False),
        "message": result.get("message", ""),
        "details": {"window": result.get("window")}
    }

def process_ai_message(message: str) -> Dict:
    """处理AI消息，根据标记调用相应的服务"""
    actions = _parse_actions(message)
    results = []

    if actions["OPENCMD"]:
        logger.info(f"检测到OPENCMD命令: {actions['OPENCMD']}")
        results.append(_handle_opencmd(actions["OPENCMD"]))

    if actions["TOPWINDOWS"]:
        logger.info(f"检测到TOPWINDOWS命令: {actions['TOPWINDOWS']}")
        results.append(_handle_topwindows(actions["TOPWINDOWS"]))

    return {
        "success": all(r["success"] for r in results) if results else True,
        "message": "处理完成" if results else "未检测到任何操作",
        "results": results
    }

@app.post("/process_ai_message")
async def process_ai_message_endpoint(payload: dict = Body(...)):
    """
    处理AI消息，根据标记调用相应的服务

    参数:
        payload: 包含AI回答的字典
        {
            "message": "AI的回答内容，可能包含[ACTION:OPENCMD]、[ACTION:RUN]或[ACTION:BG]标记"
        }

    返回:
        {
            "success": True/False,
            "message": "操作结果描述",
            "results": [
                {
                    "action": "操作类型",
                    "success": True/False,
                    "message": "操作结果描述",
                    "details": {...}
                },
                ...
            ]
        }
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
    logger.info("启动命令执行服务...")
    uvicorn.run(app, host="0.0.0.0", port=8008)
