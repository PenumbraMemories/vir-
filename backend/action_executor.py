#执行TOPWINDOWS
#执行终端命令捕获输出[OPENCMD]
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
import subprocess
import re
import win32gui
import win32con
import win32process
import win32api
from typing import Dict, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
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

def execute_command(command: str) -> Dict:
    """
    执行终端命令并捕获输出

    Args:
        command: 要执行的命令

    Returns:
        Dict: 包含执行结果的字典
    """
    try:
        logger.info(f"执行命令: {command}")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
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

def set_window_topmost(window_title: str) -> Dict:
    """
    根据窗口标题置顶窗口

    Args:
        window_title: 要置顶的窗口标题（可以是部分匹配）

    Returns:
        Dict: 操作结果
    """
    try:
        # 获取所有窗口
        windows = []
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                windows.append({
                    "handle": hwnd,
                    "title": title,
                    "class_name": class_name
                })
            return True
        win32gui.EnumWindows(enum_windows_callback, None)

        # 查找匹配的窗口
        matched_window = None
        for window in windows:
            if window_title.lower() in window["title"].lower():
                matched_window = window
                break

        if not matched_window:
            return {
                "success": False,
                "message": f"未找到标题包含 '{window_title}' 的窗口",
                "window": None
            }

        # 置顶窗口
        # 先确保窗口可见
        if not win32gui.IsWindowVisible(matched_window["handle"]):
            win32gui.ShowWindow(matched_window["handle"], win32con.SW_RESTORE)

        # 强制显示窗口
        win32gui.ShowWindow(matched_window["handle"], win32con.SW_SHOW)
        win32gui.ShowWindow(matched_window["handle"], win32con.SW_RESTORE)

        # 获取当前前台窗口的线程ID
        foreground_thread = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[0]
        current_thread = win32api.GetCurrentThreadId()

        # 附加到前台窗口的线程
        if foreground_thread != current_thread:
            win32process.AttachThreadInput(current_thread, foreground_thread, True)

        try:
            # 模拟按下Alt键，绕过焦点限制
            win32api.keybd_event(0x12, 0, 0, 0)  # ALT down

            # 设置窗口为最顶层
            win32gui.SetWindowPos(
                matched_window["handle"],
                win32con.HWND_TOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
            )

            # 释放Alt键
            win32api.keybd_event(0x12, 0, 2, 0)  # ALT up

            # 强制激活窗口（带错误处理）
            try:
                win32gui.SetFocus(matched_window["handle"])
            except:
                pass

            try:
                win32gui.SetActiveWindow(matched_window["handle"])
            except:
                pass

            win32gui.SetForegroundWindow(matched_window["handle"])
            win32gui.BringWindowToTop(matched_window["handle"])

            # 强制刷新窗口
            win32gui.UpdateWindow(matched_window["handle"])
            win32gui.InvalidateRect(matched_window["handle"], None, True)

            # 再次确保窗口可见
            win32gui.ShowWindow(matched_window["handle"], win32con.SW_SHOW)
        finally:
            # 分离线程
            if foreground_thread != current_thread:
                win32process.AttachThreadInput(current_thread, foreground_thread, False)

        return {
            "success": True,
            "message": f"成功置顶窗口: {matched_window['title']}",
            "window": {
                "handle": matched_window["handle"],
                "title": matched_window["title"],
                "class_name": matched_window["class_name"]
            }
        }
    except Exception as e:
        logger.error(f"置顶窗口失败: {str(e)}")
        return {
            "success": False,
            "message": f"置顶窗口失败: {str(e)}",
            "window": None
        }

def parse_ai_actions(message: str) -> Dict:
    """
    解析AI回复中的操作标记

    Args:
        message: AI返回的消息内容

    Returns:
        Dict: 包含解析出的操作和参数
    """
    actions = {"OPENCMD": None, "TOPWINDOWS": None}
    opencmd_pattern = r'\[ACTION:OPENCMD\](.*?)(?=\[ACTION|$)'
    opencmd_matches = re.findall(opencmd_pattern, message)
    actions["OPENCMD"] = opencmd_matches[0].strip() if opencmd_matches else None

    # 提取要置顶的窗口名称
    window_pattern = r'\[ACTION:TOPWINDOWS\](.*?)(?=\[ACTION|$)'
    window_match = re.search(window_pattern, message)
    actions["TOPWINDOWS"] = window_match.group(1).strip() if window_match else None

    return actions

def process_ai_message(message: str) -> Dict:
    """
    处理AI消息，根据标记调用相应的服务

    Args:
        message: AI返回的消息内容

    Returns:
        Dict: 处理结果
    """
    actions = parse_ai_actions(message)
    results = []

    # 处理OPENCMD命令
    if actions["OPENCMD"]:
        logger.info(f"检测到OPENCMD命令: {actions['OPENCMD']}")
        result = execute_command(actions["OPENCMD"])
        results.append({
            "action": "execute_command",
            "success": result.get("success", False),
            "message": "命令执行成功" if result.get("success") else "命令执行失败",
            "details": {
                "command": actions["OPENCMD"],
                "stdout": result.get("stdout"),
                "stderr": result.get("stderr"),
                "returncode": result.get("returncode")
            }
        })

    # 处理置顶窗口操作
    if actions["TOPWINDOWS"]:
        logger.info(f"检测到置顶窗口操作: {actions['TOPWINDOWS']}")
        result = set_window_topmost(actions["TOPWINDOWS"])
        results.append({
            "action": "set_window_topmost",
            "success": result.get("success", False),
            "message": result.get("message", ""),
            "details": {
                "window": result.get("window")
            }
        })

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
