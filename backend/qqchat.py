import win32gui
import win32con
import win32api
import win32clipboard
import time
import re
import os
import logging
from ctypes import wintypes
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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

def find_qq_window():
    """查找QQ窗口（支持新版QQ）"""
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            # 新版QQ的窗口标题是"QQ"，类名是Chrome_WidgetWin_1
            if window_text == "QQ" and class_name == "Chrome_WidgetWin_1":
                windows.append(hwnd)
        return True

    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows[0] if windows else None

def find_chat_window_by_friend(friend_name):
    """通过好友名查找聊天窗口（支持新版QQ）"""
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            
            # 新版QQ聊天窗口的特征
            # 1. 窗口标题包含好友名称
            # 2. 类名是Chrome_WidgetWin_1
            # 3. 不是主QQ窗口（主窗口标题是"QQ"）
            if friend_name in window_text and class_name == "Chrome_WidgetWin_1" and window_text != "QQ":
                windows.append(hwnd)
                logger.info(f"找到聊天窗口: '{window_text}' (类名: {class_name})")
        return True

    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows[0] if windows else None

def activate_window(hwnd, max_retries=3):
    """激活窗口并确保其获得焦点"""
    for i in range(max_retries):
        try:
            # 如果窗口最小化，先恢复
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.3)
            
            # 显示窗口
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            time.sleep(0.1)
            
            # 尝试设置前台窗口
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)
            time.sleep(0.3)
            
            # 验证窗口是否成功激活
            foreground_hwnd = win32gui.GetForegroundWindow()
            if foreground_hwnd == hwnd:
                logger.info(f"窗口激活成功: {win32gui.GetWindowText(hwnd)}")
                return True
            else:
                logger.warning(f"窗口激活尝试 {i+1}/{max_retries} 失败")
                # 使用Alt+Tab尝试切换
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"激活窗口失败: {e}")
        
        time.sleep(0.5)
    
    return False

def click_input_area(hwnd):
    """点击聊天窗口的输入区域"""
    try:
        # 获取窗口位置
        rect = win32gui.GetWindowRect(hwnd)
        # 计算输入区域位置（窗口底部向上约100像素，中间偏左）
        x = rect[0] + (rect[2] - rect[0]) // 2
        y = rect[3] - 100
        
        logger.info(f"点击输入区域: ({x}, {y}), 窗口区域: {rect}")
        
        # 移动鼠标并点击
        win32api.SetCursorPos((x, y))
        time.sleep(0.2)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.3)
        
        return True
    except Exception as e:
        logger.error(f"点击输入区域失败: {e}")
        return False

def search_and_open_chat(hwnd, friend_name):
    """搜索好友并打开聊天窗口（适配新版QQ）"""
    logger.info(f"正在搜索好友: {friend_name}")
    
    # 激活QQ主窗口
    if not activate_window(hwnd):
        logger.error("无法激活QQ主窗口")
        return False
    
    time.sleep(0.5)
    
    # 新版QQ使用Ctrl+F打开搜索
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(ord('F'), 0x21, 0, 0)
    time.sleep(0.2)
    win32api.keybd_event(ord('F'), 0x21, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.5)

    # 清空搜索框（Ctrl+A然后Delete）
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(ord('A'), 0x1E, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(ord('A'), 0x1E, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)
    win32api.keybd_event(win32con.VK_DELETE, 0x2E, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(win32con.VK_DELETE, 0x2E, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)

    # 输入好友名称
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(friend_name, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(ord('V'), 0x2F, 0, 0)
    time.sleep(0.2)
    win32api.keybd_event(ord('V'), 0x2F, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(1.0)

    # 等待搜索结果出现，然后按回车打开聊天窗口
    time.sleep(0.5)
    win32api.keybd_event(win32con.VK_RETURN, 0x1C, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(win32con.VK_RETURN, 0x1C, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(1.0)  # 等待聊天窗口打开
    
    return True

def send_message_to_chat(message):
    """向当前激活的聊天窗口发送消息"""
    # 先确保当前窗口有焦点，点击输入区域
    foreground_hwnd = win32gui.GetForegroundWindow()
    if foreground_hwnd:
        click_input_area(foreground_hwnd)
    
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(message, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(ord('V'), 0x2F, 0, 0)
    time.sleep(0.2)
    win32api.keybd_event(ord('V'), 0x2F, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)

    win32api.keybd_event(win32con.VK_RETURN, 0x1C, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(win32con.VK_RETURN, 0x1C, win32con.KEYEVENTF_KEYUP, 0)

    return True

def validate_file_path(file_path: str) -> str:
    """验证并规范化文件路径，支持相对路径和常见位置查找"""
    try:
        # 去除首尾空格和引号
        file_path = file_path.strip().strip('"').strip("'")
        
        # 如果已经是绝对路径且存在，直接返回
        abs_path = os.path.abspath(file_path)
        if os.path.exists(abs_path):
            logger.info(f"找到文件: {abs_path}")
            return abs_path
        
        # 定义常见搜索路径
        common_paths = [
            os.environ.get('USERPROFILE', ''),  # 用户目录
            os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),  # 桌面
            os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads'),  # 下载
            os.path.join(os.environ.get('USERPROFILE', ''), 'Documents'),  # 文档
            os.getcwd(),  # 当前工作目录
        ]
        
        # 获取文件名（如果输入是相对路径）
        file_name = os.path.basename(file_path)
        
        # 在所有常见路径中搜索
        for search_path in common_paths:
            if not search_path:
                continue
            
            # 尝试组合完整路径
            candidate = os.path.join(search_path, file_name)
            if os.path.exists(candidate):
                logger.info(f"在 {search_path} 找到文件: {candidate}")
                return candidate
            
            # 尝试原路径组合
            candidate2 = os.path.join(search_path, file_path)
            if os.path.exists(candidate2):
                logger.info(f"在 {search_path} 找到文件: {candidate2}")
                return candidate2
        
        # 尝试使用 glob 模式匹配（支持通配符）
        import glob
        for search_path in common_paths:
            if not search_path:
                continue
            pattern = os.path.join(search_path, file_name)
            matches = glob.glob(pattern)
            if matches:
                logger.info(f"通过模式匹配找到文件: {matches[0]}")
                return matches[0]
        
        logger.warning(f"找不到文件: {file_path}")
        return None
        
    except Exception as e:
        logger.error(f"验证文件路径时出错: {e}")
        return None

def copy_file_to_clipboard(file_path: str) -> bool:
    """复制文件到剪贴板"""
    try:
        logger.info(f"正在复制文件: {file_path}")
        
        # 验证文件存在
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return False
        
        # 方法1：使用更可靠的方式打开文件管理器并选中文件
        # 使用 /select 参数打开文件管理器并选中文件
        os.system(f'explorer /select,"{file_path}"')
        time.sleep(1.5)

        # 查找文件窗口（尝试多个类名）
        file_window = None
        start_time = time.time()
        window_classes = ["CabinetWClass", "ExploreWClass", "Progman", "Shell_TrayWnd"]
        
        while time.time() - start_time < 5:
            for class_name in window_classes:
                file_window = win32gui.FindWindow(class_name, None)
                if file_window and win32gui.IsWindowVisible(file_window):
                    break
            if file_window:
                break
            time.sleep(0.5)
            
        if not file_window:
            logger.warning("未找到文件窗口，尝试直接复制文件路径")
            # 备用方案：直接复制文件路径到剪贴板
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(file_path, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return True

        # 激活文件窗口
        activate_window(file_window)
        time.sleep(0.5)

        # 复制文件 (Ctrl+C)
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(ord('C'), 0x2E, 0, 0)
        time.sleep(0.2)
        win32api.keybd_event(ord('C'), 0x2E, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1.0)

        # 关闭文件资源管理器
        win32gui.PostMessage(file_window, win32con.WM_CLOSE, 0, 0)
        time.sleep(0.5)

        logger.info("文件复制成功")
        return True
    except Exception as e:
        logger.error(f"复制文件失败: {e}", exc_info=True)
        return False

def paste_and_send_file_to_chat(chat_hwnd=None) -> bool:
    """在聊天窗口中粘贴并发送文件"""
    try:
        if not chat_hwnd:
            chat_hwnd = win32gui.GetForegroundWindow()
        
        # 确保聊天窗口是激活状态
        logger.info("确保聊天窗口激活...")
        activate_window(chat_hwnd)
        time.sleep(0.5)
        
        # 点击输入区域确保焦点
        logger.info("点击输入区域...")
        click_input_area(chat_hwnd)
        time.sleep(0.5)
        
        # 粘贴文件 (Ctrl+V)
        logger.info("粘贴文件...")
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(ord('V'), 0x2F, 0, 0)
        time.sleep(0.2)
        win32api.keybd_event(ord('V'), 0x2F, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1.5)  # 增加等待时间，让文件上传

        # 发送文件 (回车)
        logger.info("发送文件...")
        win32api.keybd_event(win32con.VK_RETURN, 0x1C, 0, 0)
        time.sleep(0.2)
        win32api.keybd_event(win32con.VK_RETURN, 0x1C, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1.0)

        logger.info("文件粘贴并发送成功")
        return True
    except Exception as e:
        logger.error(f"粘贴发送文件失败: {e}", exc_info=True)
        return False

def send_qq_file_with_full_flow(friend_name, file_path):
    """完整的发送文件流程"""
    logger.info(f"开始完整流程发送文件给 {friend_name}: {file_path}")
    
    # 步骤0：验证文件路径
    validated_path = validate_file_path(file_path)
    if not validated_path:
        logger.error(f"文件路径无效: {file_path}")
        return False
    
    logger.info(f"使用文件: {validated_path}")
    
    # 步骤1：查找QQ主窗口
    qq_hwnd = find_qq_window()
    if not qq_hwnd:
        logger.error("未找到QQ窗口，请确保QQ已运行")
        return False

    try:
        # 步骤2：搜索好友并打开聊天窗口
        logger.info(f"步骤1: 搜索好友 {friend_name}")
        if not search_and_open_chat(qq_hwnd, friend_name):
            logger.error("打开聊天窗口失败")
            return False
        
        # 步骤3：查找聊天窗口
        logger.info("步骤2: 查找聊天窗口")
        chat_hwnd = None
        for attempt in range(15):  # 尝试15次
            time.sleep(1)
            chat_hwnd = find_chat_window_by_friend(friend_name)
            if chat_hwnd:
                logger.info(f"找到聊天窗口 (尝试 {attempt+1}/15)")
                break
            else:
                logger.info(f"等待聊天窗口打开... (尝试 {attempt+1}/15)")
        
        if not chat_hwnd:
            # 如果还是找不到，尝试获取当前激活的窗口
            chat_hwnd = win32gui.GetForegroundWindow()
            window_text = win32gui.GetWindowText(chat_hwnd)
            if friend_name in window_text:
                logger.info(f"使用当前激活窗口: {window_text}")
            else:
                logger.error(f"未找到 {friend_name} 的聊天窗口")
                return False
        
        # 步骤4：复制文件
        logger.info(f"步骤3: 复制文件 {validated_path}")
        if not copy_file_to_clipboard(validated_path):
            logger.error("复制文件失败")
            return False
        
        # 步骤5：切换到聊天窗口并发送
        logger.info("步骤4: 切换到聊天窗口")
        activate_window(chat_hwnd)
        time.sleep(0.5)
        
        logger.info("步骤5: 粘贴并发送文件")
        if not paste_and_send_file_to_chat(chat_hwnd):
            logger.error("粘贴发送文件失败")
            return False
        
        logger.info(f"文件已成功发送给 {friend_name}")
        return True
        
    except Exception as e:
        logger.error(f"发送文件失败: {e}", exc_info=True)
        return False

def send_qq_message_advanced(friend_name, message):
    """发送QQ消息"""
    # 先尝试查找已存在的聊天窗口
    chat_hwnd = find_chat_window_by_friend(friend_name)
    
    if chat_hwnd:
        logger.info(f"找到现有聊天窗口: {friend_name}")
        activate_window(chat_hwnd)
        time.sleep(0.3)
        click_input_area(chat_hwnd)
        time.sleep(0.3)
        send_message_to_chat(message)
        return True
    
    # 如果没有找到，打开新聊天窗口
    qq_hwnd = find_qq_window()
    if qq_hwnd:
        logger.info(f"未找到 {friend_name} 的聊天窗口，正在打开...")
        search_and_open_chat(qq_hwnd, friend_name)
        time.sleep(1.0)
        
        # 获取新打开的聊天窗口
        chat_hwnd = find_chat_window_by_friend(friend_name)
        if not chat_hwnd:
            chat_hwnd = win32gui.GetForegroundWindow()
        
        click_input_area(chat_hwnd)
        send_message_to_chat(message)
        return True
    
    return False

def parse_ai_response(ai_text):
    """解析AI返回的文本，包含路径验证"""
    result = {
        'messages': [],
        'files': []
    }

    # 添加日志输出原始文本
    logger.info(f"解析AI响应，原始文本: {ai_text[:500]}...")

    friend_pattern = r'\[ACTION:SELECTFRIEND\](.*?)(?=\[ACTION|$)'
    message_pattern = r'\[ACTION:SENDMESSAGE\](.*?)(?=\[ACTION|$)'
    file_pattern = r'\[ACTION:SENDFILE\](.*?)(?=\[ACTION|$)'

    friend_matches = re.findall(friend_pattern, ai_text)
    message_matches = re.findall(message_pattern, ai_text)
    file_matches = re.findall(file_pattern, ai_text)

    # 添加日志输出匹配结果
    logger.info(f"好友匹配结果: {friend_matches}")
    logger.info(f"消息匹配结果: {message_matches}")
    logger.info(f"文件匹配结果: {file_matches}")

    # 处理消息
    if friend_matches and message_matches:
        min_length = min(len(friend_matches), len(message_matches))
        for i in range(min_length):
            friend_name = friend_matches[i].strip()
            message = message_matches[i].strip()
            result['messages'].append((friend_name, message))
            logger.info(f"解析到消息: 发送给 {friend_name} -> {message[:50]}...")

    # 处理文件，包含路径验证
    if friend_matches and file_matches:
        min_length = min(len(friend_matches), len(file_matches))
        for i in range(min_length):
            friend_name = friend_matches[i].strip()
            file_path = file_matches[i].strip()
            
            # 验证文件路径
            validated_path = validate_file_path(file_path)
            if validated_path:
                result['files'].append((friend_name, validated_path))
                logger.info(f"解析到文件: 发送给 {friend_name} -> {validated_path}")
            else:
                logger.warning(f"文件路径无效，跳过: {file_path}")
                
    elif file_matches and not friend_matches:
        # 如果没有指定好友，使用最后一条消息的好友
        if result['messages']:
            last_friend = result['messages'][-1][0]
            for file_path in file_matches:
                validated_path = validate_file_path(file_path.strip())
                if validated_path:
                    result['files'].append((last_friend, validated_path))
                    logger.info(f"解析到文件（使用最后好友）: 发送给 {last_friend} -> {validated_path}")
                else:
                    logger.warning(f"文件路径无效，跳过: {file_path}")
        else:
            # 完全没有好友信息，记录错误
            logger.error("解析文件操作时未找到好友信息")

    # 输出解析结果统计
    logger.info(f"解析完成: 消息数量={len(result['messages'])}, 文件数量={len(result['files'])}")
    
    return result

def process_ai_commands(ai_text):
    """处理AI命令"""
    result = parse_ai_response(ai_text)
    results = []
    success_count = 0

    # 发送消息
    for friend_name, message in result['messages']:
        logger.info(f"发送消息给 {friend_name}: {message[:100]}...")
        if send_qq_message_advanced(friend_name, message):
            success_count += 1
            results.append({'type': 'message', 'friend': friend_name, 'success': True, 'message': message[:100]})
        else:
            results.append({'type': 'message', 'friend': friend_name, 'success': False, 'message': message[:100]})
            logger.error(f"发送消息失败: {friend_name}")

    # 发送文件
    for friend_name, file_path in result['files']:
        logger.info(f"发送文件给 {friend_name}: {file_path}")
        if send_qq_file_with_full_flow(friend_name, file_path):
            success_count += 1
            results.append({'type': 'file', 'friend': friend_name, 'success': True, 'file': file_path})
        else:
            results.append({'type': 'file', 'friend': friend_name, 'success': False, 'file': file_path})
            logger.error(f"发送文件失败: {friend_name} -> {file_path}")

    logger.info(f"完成，成功: {success_count}/{len(results)}")
    return results

@app.post("/send_qq_message")
async def send_qq_message_endpoint(payload: dict = Body(...)):
    """处理AI消息并发送QQ消息和文件"""
    try:
        message = payload.get("message", "")
        if not message:
            return {"success": False, "message": "未提供消息内容", "results": []}

        logger.info(f"收到请求，消息内容: {message[:200]}...")
        results = process_ai_commands(message)
        
        if not results:
            return {"success": False, "message": "未能从AI响应中解析出任何操作", "results": []}

        success_count = sum(1 for r in results if r['success'])
        return {
            "success": success_count > 0,
            "message": f"成功执行 {success_count}/{len(results)} 个操作",
            "results": results
        }
    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)
        return {"success": False, "message": f"处理失败: {str(e)}", "results": []}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "QQ Message Service"}

if __name__ == "__main__":
    import uvicorn
    print("启动QQ消息服务...")
    print("服务地址: http://0.0.0.0:8002")
    print("API文档: http://0.0.0.0:8002/docs")
    uvicorn.run(app, host="0.0.0.0", port=8002)