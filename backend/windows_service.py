
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
import win32gui
import win32con
import win32process
import win32api
import re
import requests
import time
import asyncio
from typing import Dict, Optional, List


# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 命令队列
action_queue = asyncio.Queue()
queue_processor_task = None

async def action_queue_processor():
    """
    异步处理命令队列中的命令
    """
    global queue_processor_task
    logger.info("启动命令队列处理器")
    
    while True:
        try:
            # 从队列中获取命令
            action_data = await action_queue.get()
            logger.info(f"从队列中获取命令: {action_data['action_type']}")
            
            # 执行命令
            action_type = action_data['action_type']
            if action_type == "TOPWINDOWS":
                result = set_window_topmost(action_data['params']['window_title'])
                action_data['result_queue'].put_nowait({
                    "action": "set_window_topmost",
                    "success": result.get("success", False),
                    "message": result.get("message", ""),
                    "details": {
                        "window": result.get("window")
                    }
                })
            elif action_type == "SCREENSHOT":
                result = call_screenshot_service(action_data['params']['message'])
                action_data['result_queue'].put_nowait({
                    "action": "screenshot",
                    "success": result.get("success", False),
                    "message": result.get("message", ""),
                    "details": {
                        "screenshot_path": result.get("screenshot_path"),
                        "screenshot_url": result.get("screenshot_url")
                    }
                })
            elif action_type == "NOWWINDOWS":
                try:
                    windows = get_all_windows()
                    action_data['result_queue'].put_nowait({
                        "action": "get_windows",
                        "success": True,
                        "message": f"成功获取 {len(windows)} 个窗口",
                        "details": {
                            "windows": windows
                        }
                    })
                except Exception as e:
                    logger.error(f"获取窗口失败: {str(e)}")
                    action_data['result_queue'].put_nowait({
                        "action": "get_windows",
                        "success": False,
                        "message": f"获取窗口失败: {str(e)}",
                        "details": None
                    })
            
            # 标记任务完成
            action_queue.task_done()
            logger.info(f"命令执行完成: {action_type}")

            # 等待1秒再处理下一个命令
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"处理命令队列时发生错误: {str(e)}", exc_info=True)

async def start_queue_processor():
    """
    启动命令队列处理器
    """
    global queue_processor_task
    if queue_processor_task is None or queue_processor_task.done():
        queue_processor_task = asyncio.create_task(action_queue_processor())
        logger.info("命令队列处理器已启动")

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

            # 取消置顶状态，使窗口不再保持置顶
            win32gui.SetWindowPos(
                matched_window["handle"],
                win32con.HWND_NOTOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
            )

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
async def get_windows(payload: dict = Body(...)):
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

# QQ消息服务配置
QQ_CHAT_SERVICE_URL = "http://localhost:8002"

# 截图服务配置
SCREENSHOT_SERVICE_URL = "http://localhost:8003"

def call_qq_chat_service(message: str) -> Dict:
    """
    调用QQ聊天服务
    
    Args:
        message: AI返回的消息内容
        
    Returns:
        Dict: 服务返回的结果
    """
    try:
        response = requests.post(
            f"{QQ_CHAT_SERVICE_URL}/send_qq_message",
            json={"message": message},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"调用QQ聊天服务失败: {str(e)}")
        return {
            "success": False,
            "message": f"调用QQ聊天服务失败: {str(e)}",
            "friend": None,
            "content": None
        }

def call_screenshot_service(message: str) -> Dict:
    """
    调用截图服务
    
    Args:
        message: 包含截图指令的消息
        
    Returns:
        Dict: 服务返回的结果
    """
    try:
        response = requests.post(
            f"{SCREENSHOT_SERVICE_URL}/screenshot",
            json={"message": message},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"调用截图服务失败: {str(e)}")
        return {
            "success": False,
            "message": f"调用截图服务失败: {str(e)}",
            "screenshot_path": None,
            "screenshot_url": None
        }

def parse_ai_actions(message: str) -> Dict:
    """
    解析AI回复中的操作标记
    
    Args:
        message: AI返回的消息内容
        
    Returns:
        Dict: 包含解析出的操作和参数
    """
    actions = {
        "SENDMESSAGE": False,
        "SELECTFRIEND": False,
        "NOWWINDOWS": False,
        "SCREENSHOT": False,
        "TOPWINDOWS": False
    }
    
    # 提取好友名称
    friend_pattern = r'\[ACTION:SELECTFRIEND\](.*?)(?=\[ACTION|$)'
    friend_match = re.search(friend_pattern, message)
    actions["SELECTFRIEND"] = friend_match.group(1).strip() if friend_match else None
    
    # 提取消息内容
    message_pattern = r'\[ACTION:SENDMESSAGE\](.*?)(?=\[ACTION|$)'
    message_match = re.search(message_pattern, message)
    actions["SENDMESSAGE"] = message_match.group(1).strip() if message_match else None
    
    # 检查是否包含获取窗口指令
    actions["NOWWINDOWS"] = "[ACTION:NOWWINDOWS]" in message
    
    # 检查是否包含截图指令
    actions["SCREENSHOT"] = "[ACTION:SCREENSHOT]" in message
    
    # 提取要置顶的窗口名称
    window_pattern = r'\[ACTION:TOPWINDOWS\](.*?)(?=\[ACTION|$)'
    window_match = re.search(window_pattern, message)
    actions["TOPWINDOWS"] = window_match.group(1).strip() if window_match else None

    return actions

async def process_ai_message(message: str) -> Dict:
    """
    处理AI消息，根据标记调用相应的服务
    
    Args:
        message: AI返回的消息内容
        
    Returns:
        Dict: 处理结果
    """
    # 确保队列处理器已启动
    await start_queue_processor()
    
    actions = parse_ai_actions(message)
    results = []
    
    # 创建结果队列
    result_queue = asyncio.Queue()
    
    # 处理发送QQ消息操作
    if actions["SELECTFRIEND"] and actions["SENDMESSAGE"]:
        logger.info("检测到发送QQ消息操作")
        result = call_qq_chat_service(message)
        results.append({
            "action": "send_qq_message",
            "success": result.get("success", False),
            "message": result.get("message", ""),
            "details": {
                "friend": result.get("friend"),
                "content": result.get("content")
            }
        })
    
    # 收集获取窗口操作
    if actions["NOWWINDOWS"]:
        logger.info("检测到获取窗口操作")
        serial_actions.append({
            "action_type": "NOWWINDOWS",
            "params": {},
            "result_queue": result_queue
        })
    
    # 收集截图操作
    if actions["SCREENSHOT"]:
        logger.info("检测到截图操作")
        serial_actions.append({
            "action_type": "SCREENSHOT",
            "params": {"message": message},
            "result_queue": result_queue
        })
    
    # 收集需要串行执行的命令
    serial_actions = []
    
    # 收集置顶窗口操作
    if actions["TOPWINDOWS"]:
        logger.info(f"检测到置顶窗口操作: {actions['TOPWINDOWS']}")
        serial_actions.append({
            "action_type": "TOPWINDOWS",
            "params": {"window_title": actions["TOPWINDOWS"]},
            "result_queue": result_queue
        })
    
    # 将命令添加到队列中
    for action in serial_actions:
        await action_queue.put(action)
        logger.info(f"已将命令添加到队列: {action['action_type']}")
    
    # 等待所有命令执行完成
    for _ in range(len(serial_actions)):
        result = await result_queue.get()
        results.append(result)
        logger.info(f"命令执行结果: {result['action']} - {result['success']}")

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
            "message": "AI的回答内容，可能包含[ACTION:SELECTFRIEND]和[ACTION:SENDMESSAGE]等标记"
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
        logger.debug(f"接收到的消息: {message}")
        
        if not message:
            return {
                "success": False,
                "message": "未提供消息内容",
                "results": []
            }
        
        # 处理AI消息
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
    uvicorn.run(app, host="0.0.0.0", port=8005)
