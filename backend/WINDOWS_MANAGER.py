# 8020-管理窗口

#------------------------------------------------------------------------------------------------
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
import win32gui
import win32con
import win32process
import win32api
import re
from typing import Dict, List

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



def get_all_windows() -> List[Dict]:
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
            # 只添加有标题的窗口（过滤掉空标题窗口）
            if title:
                windows.append({
                    "handle": hwnd,
                    "title": title,
                    "class_name": class_name
                })
        return True
    
    # 枚举所有窗口
    win32gui.EnumWindows(enum_windows_callback, None)
    return windows





def find_windows_by_title(window_title: str) -> List[Dict]:
    """
    根据窗口标题查找匹配的窗口
    
    Args:
        window_title: 要查找的窗口标题（支持部分匹配）
        
    Returns:
        list: 匹配的窗口列表
    """
    all_windows = get_all_windows()
    matched_windows = []
    
    for window in all_windows:
        if window_title.lower() in window["title"].lower():
            matched_windows.append(window)
    
    return matched_windows





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
    
    # 检查是否包含获取窗口列表指令
    if "[ACTION:NOWWINDOWS]" in message:
        actions["NOWWINDOWS"] = True
    
    # 提取要置顶的窗口名称（支持两种格式：#[ACTION:TOPWINDOWS] 和 [ACTION:TOPWINDOWS]）
    window_pattern = r'\[ACTION:TOPWINDOWS\](.*?)(?=\[ACTION|$)'
    window_match = re.search(window_pattern, message, re.DOTALL)
    if window_match:
        actions["TOPWINDOWS"] = window_match.group(1).strip()
    
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
        logger.info(f"开始置顶窗口，搜索关键词: '{window_title}'")
        
        # 获取所有窗口
        windows = get_all_windows()
        logger.debug(f"找到 {len(windows)} 个可见窗口")
        
        # 查找匹配的窗口
        matched_windows = find_windows_by_title(window_title)
        
        if not matched_windows:
            # 记录所有窗口标题用于调试
            all_titles = [w["title"] for w in windows]
            logger.debug(f"所有窗口标题: {all_titles}")
            return {
                "success": False,
                "message": f"未找到标题包含 '{window_title}' 的窗口",
                "window": None,
                "available_windows": all_titles[:20]  # 返回前20个窗口标题供参考
            }
        
        # 如果有多个匹配，使用第一个
        matched_window = matched_windows[0]
        logger.info(f"找到匹配窗口: '{matched_window['title']}' (句柄: {matched_window['handle']})")
        
        # 置顶窗口
        # 先确保窗口可见
        if not win32gui.IsWindowVisible(matched_window["handle"]):
            win32gui.ShowWindow(matched_window["handle"], win32con.SW_RESTORE)
        
        # 强制显示窗口
        win32gui.ShowWindow(matched_window["handle"], win32con.SW_SHOW)
        win32gui.ShowWindow(matched_window["handle"], win32con.SW_RESTORE)
        
        # 获取当前前台窗口的线程ID
        foreground_hwnd = win32gui.GetForegroundWindow()
        foreground_thread = win32process.GetWindowThreadProcessId(foreground_hwnd)[0]
        current_thread = win32api.GetCurrentThreadId()
        
        # 附加到前台窗口的线程
        attached = False
        if foreground_thread != current_thread:
            attached = win32process.AttachThreadInput(current_thread, foreground_thread, True)
            logger.debug(f"附加线程: {attached}")
        
        try:
            # 模拟按下Alt键，绕过焦点限制
            win32api.keybd_event(0x12, 0, 0, 0)  # ALT down
            
            # 设置窗口为最顶层
            result = win32gui.SetWindowPos(
                matched_window["handle"],
                win32con.HWND_TOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
            )
            logger.debug(f"SetWindowPos结果: {result}")
            
            # 释放Alt键
            win32api.keybd_event(0x12, 0, 2, 0)  # ALT up
            
            # 强制激活窗口（带错误处理）
            try:
                win32gui.SetFocus(matched_window["handle"])
                logger.debug("设置焦点成功")
            except Exception as e:
                logger.debug(f"设置焦点失败: {e}")
            
            try:
                win32gui.SetActiveWindow(matched_window["handle"])
                logger.debug("激活窗口成功")
            except Exception as e:
                logger.debug(f"激活窗口失败: {e}")
            
            try:
                win32gui.SetForegroundWindow(matched_window["handle"])
                logger.debug("设置前台窗口成功")
            except Exception as e:
                logger.debug(f"设置前台窗口失败: {e}")
            
            win32gui.BringWindowToTop(matched_window["handle"])
            
            # 强制刷新窗口
            win32gui.UpdateWindow(matched_window["handle"])
            win32gui.InvalidateRect(matched_window["handle"], None, True)
            
            # 再次确保窗口可见
            win32gui.ShowWindow(matched_window["handle"], win32con.SW_SHOW)
            
            logger.info(f"成功置顶窗口: '{matched_window['title']}'")
            
            return {
                "success": True,
                "message": f"成功置顶窗口: {matched_window['title']}",
                "window": {
                    "handle": matched_window["handle"],
                    "title": matched_window["title"],
                    "class_name": matched_window["class_name"]
                }
            }
        finally:
            # 分离线程
            if attached:
                win32process.AttachThreadInput(current_thread, foreground_thread, False)
                logger.debug("分离线程")
                
    except Exception as e:
        logger.error(f"置顶窗口失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"置顶窗口失败: {str(e)}",
            "window": None
        }





def cancel_window_topmost(window_title: str = None, window_handle: int = None) -> Dict:
    """
    取消窗口置顶
    
    Args:
        window_title: 窗口标题（可选）
        window_handle: 窗口句柄（可选）
        
    Returns:
        Dict: 操作结果
    """
    try:
        if window_handle:
            # 直接使用句柄
            win32gui.SetWindowPos(
                window_handle,
                win32con.HWND_NOTOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
            )
            return {
                "success": True,
                "message": "成功取消窗口置顶",
                "window": {"handle": window_handle}
            }
        elif window_title:
            # 根据标题查找窗口
            matched_windows = find_windows_by_title(window_title)
            if not matched_windows:
                return {
                    "success": False,
                    "message": f"未找到标题包含 '{window_title}' 的窗口",
                    "window": None
                }
            
            for window in matched_windows:
                win32gui.SetWindowPos(
                    window["handle"],
                    win32con.HWND_NOTOPMOST,
                    0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                )
            
            return {
                "success": True,
                "message": f"成功取消 {len(matched_windows)} 个窗口的置顶状态",
                "window": matched_windows[0] if matched_windows else None
            }
        else:
            return {
                "success": False,
                "message": "需要提供窗口标题或句柄",
                "window": None
            }
    except Exception as e:
        logger.error(f"取消置顶失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"取消置顶失败: {str(e)}",
            "window": None
        }

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
        logger.info(f"接收到消息: {message[:100]}...")
        
        # 解析AI消息中的操作
        actions = parse_ai_actions(message)
        
        # 处理获取窗口列表
        if actions["NOWWINDOWS"]:
            logger.info("开始获取窗口列表...")
            windows = get_all_windows()
            logger.info(f"获取到 {len(windows)} 个窗口")
            
            return {
                "success": True,
                "message": f"成功获取 {len(windows)} 个窗口",
                "windows": windows
            }
        else:
            logger.warning("消息中不包含获取窗口指令")
            return {
                "success": False,
                "message": "消息中不包含 [ACTION:NOWWINDOWS] 指令",
                "windows": None
            }
            
    except Exception as e:
        logger.error(f"获取窗口时发生错误: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"获取窗口失败: {str(e)}",
            "windows": None
        }

@app.post("/top_window")
async def top_window_endpoint(payload: dict = Body(...)):
    """
    置顶指定窗口
    
    参数:
        payload: 包含窗口标题的字典
        {
            "window_title": "要置顶的窗口标题",
            "message": "或者直接传入AI消息（会从中解析）"
        }
        
    返回:
        {
            "success": True/False,
            "message": "操作结果描述",
            "window": {...}
        }
    """
    try:
        window_title = payload.get("window_title")
        message = payload.get("message", "")
        
        # 如果没有直接提供window_title，从message中解析
        if not window_title and message:
            actions = parse_ai_actions(message)
            window_title = actions.get("TOPWINDOWS")
        
        if not window_title:
            return {
                "success": False,
                "message": "未提供窗口标题或#[ACTION:TOPWINDOWS]指令",
                "window": None
            }
        
        logger.info(f"处理置顶窗口请求: '{window_title}'")
        result = set_window_topmost(window_title)
        return result
        
    except Exception as e:
        logger.error(f"置顶窗口请求失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"处理失败: {str(e)}",
            "window": None
        }


if __name__ == "__main__":
    import uvicorn
    logger.info("=" * 50)
    logger.info("启动窗口管理器服务...")
    logger.info("服务端口: 8020")
  
    uvicorn.run(app, host="0.0.0.0", port=8020)