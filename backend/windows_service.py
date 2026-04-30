#[ACTION:TOPWINDOWS]
#[ACTION:NOWWINDOWS]
#8020
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
import win32gui
import win32con
import win32process
import win32api
import re
from typing import Dict


# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_all_windows():
    """
    获取所有可见窗口的标题和类名

    返回:
        list: 窗口信息列表，每个元素包含handle, title, class_name
    """
    windows = []

    def enum_windows_callback(hwnd, _):
        # 检查窗口是否可见
        if win32gui.IsWindowVisible(hwnd):
            # 获取窗口标题
            title = win32gui.GetWindowText(hwnd)
            # 获取窗口类名
            class_name = win32gui.GetClassName(hwnd)
            # 添加到结果列表
            windows.append({
                "handle": hwnd,
                "title": title,
                "class_name": class_name
            })
        return True

    # 枚举所有窗口
    win32gui.EnumWindows(enum_windows_callback, None)
    return windows

def parse_ai_actions(message: str) -> Dict:
    """
    解析AI回复中的窗口操作标记

    Args:
        message: AI返回的消息内容

    Returns:
        Dict: 包含解析出的操作和参数
    """
    actions = {
        "NOWWINDOWS": False,
        "TOPWINDOWS": None
    }

   

    # 提取要置顶的窗口名称
    window_pattern = r'\[ACTION:TOPWINDOWS\](.*?)(?=\[ACTION|$)'
    window_match = re.search(window_pattern, message)
    actions["TOPWINDOWS"] = window_match.group(1).strip() if window_match else None

    return actions

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
        windows = get_all_windows()

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

app = FastAPI()

# 添加CORS中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get_windows")
async def get_windows_endpoint(payload: dict = Body(...)):
    """
    获取所有可见窗口的标题和类名

    参数:
        payload: 包含AI回答的字典
        {
            "message": "AI的回答内容"
        }

    返回:
        {
            "success": True/False,
            "message": "操作结果描述",
            "windows": [
                {
                    "handle": 窗口句柄,
                    "title": "窗口标题",
                    "class_name": "窗口类名"
                },
                ...
            ]
        }
    """
    try:
        message = payload.get("message", "")
        logger.debug(f"接收到的消息: {message}")

        # 检查消息中是否包含获取窗口指令
        if "[ACTION:NOWWINDOWS]" not in message:
            logger.warning("消息中不包含获取窗口指令")
            return {
                "success": False,
                "message": "消息中不包含获取窗口指令",
                "windows": None
            }

        logger.info("开始获取窗口列表...")
        # 获取所有窗口
        windows = get_all_windows()
        logger.debug(f"获取到 {len(windows)} 个窗口")

        # 记录每个窗口的信息
        for idx, window in enumerate(windows):
            logger.debug(f"窗口 {idx + 1}: 句柄={window.get('handle')}, 标题={window.get('title')}, 类名={window.get('class_name')}")

        # 返回结果
        result = {
            "success": True,
            "message": f"成功获取 {len(windows)} 个窗口",
            "windows": windows
        }
        logger.info(f"成功返回 {len(windows)} 个窗口信息")
        return result

    except Exception as e:
        logger.error(f"获取窗口时发生错误: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"获取窗口失败: {str(e)}",
            "windows": None
        }





if __name__ == "__main__":
    import uvicorn
    logger.info("启动窗口服务...")
    uvicorn.run(app, host="0.0.0.0", port=8020)
