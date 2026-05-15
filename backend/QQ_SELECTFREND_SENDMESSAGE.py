# 8021-QQ消息发送服务
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
import win32con
import win32api
import win32gui
import time
import re
import pyperclip

from typing import Dict, Optional
from pydantic import BaseModel

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

class MessageRequest(BaseModel):
    """消息请求模型"""
    message: str
    delay: Optional[int] = 0






def find_and_click_search_button() -> bool:
    """使用Ctrl+F快捷键打开搜索栏"""
    try:
      
        
         
        logger.warning("使用Ctrl+F快捷键")
        
        # 使用更安全的按键发送方式
        # 先确保焦点在正确位置
        time.sleep(0.1)
        
        # 发送Ctrl+F
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('F'), 0x21, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('F'), 0x21, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)
        
        return True
        
    except Exception as e:
        logger.error(f"打开搜索框失败: {e}")
        return False


def send_text_message(message: str) -> bool:
    """使用剪贴板方式在当前激活的聊天窗口中发送文本消息"""
    try:
        if not message or not message.strip():
            logger.error("消息内容不能为空")
            return False
        
        logger.info(f"准备发送消息: {message[:50]}...")
        
    
        # 使用 pyperclip 复制文本到剪贴板
        pyperclip.copy(message)
        logger.info("文本已复制到剪贴板")
        time.sleep(0.2)
        
        # 粘贴文本 (Ctrl+V)
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        # 发送消息 (回车)
        win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        logger.info("消息发送成功")
        return True
        
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return False


def select_friend(friend_name: str) -> Dict:
    """在搜索栏中搜索并选择QQ好友"""
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
        return {
            "success": True,
            "message": f"成功选择好友: {friend_name}"
        }
        
    except Exception as e:
        logger.error(f"选择好友失败: {e}")
        return {
            "success": False,
            "message": f"选择好友失败: {str(e)}"
        }


def parse_selectfriend_sendmessage_action(message: str) -> Dict:
    """解析 [ACTION:SELECTFRIEND_SENDMESSAGE] 指令"""
    try:
        # 匹配指令格式
        pattern = r'\[ACTION:SELECTFRIEND_SENDMESSAGE\](.*?)(?=\[ACTION|$)'
        match = re.search(pattern, message, re.DOTALL)
        
        if not match:
            return {
                "has_action": False,
                "friend_name": None,
                "message_content": None
            }
        
        content = match.group(1).strip()
        logger.info(f"解析指令内容: {content}")
        
        # 使用竖线分隔好友名称和消息内容
        if '|' in content:
            parts = content.split('|', 1)
            friend_name = parts[0].strip()
            message_content = parts[1].strip()
        elif '｜' in content:  # 全角竖线
            parts = content.split('｜', 1)
            friend_name = parts[0].strip()
            message_content = parts[1].strip()
        elif '；' in content:  # 中文分号
            parts = content.split('；', 1)
            friend_name = parts[0].strip()
            message_content = parts[1].strip()
        elif ';' in content:  # 英文分号
            parts = content.split(';', 1)
            friend_name = parts[0].strip()
            message_content = parts[1].strip()
        else:
            logger.warning(f"无法解析指令内容，缺少分隔符: {content}")
            return {
                "has_action": True,
                "friend_name": None,
                "message_content": None,
                "parse_error": "格式错误，正确格式: 好友名称|消息内容"
            }
        
        if not friend_name or not message_content:
            return {
                "has_action": True,
                "friend_name": friend_name,
                "message_content": message_content,
                "parse_error": "好友名称或消息内容不能为空"
            }
        
        return {
            "has_action": True,
            "friend_name": friend_name,
            "message_content": message_content
        }
        
    except Exception as e:
        logger.error(f"解析指令失败: {e}")
        return {
            "has_action": False,
            "friend_name": None,
            "message_content": None,
            "parse_error": str(e)
        }


def execute_selectfriend_sendmessage(friend_name: str, message_content: str, delay: int = 0) -> Dict:
    """执行选择好友并发送消息的操作"""
    results = []
    
    if delay > 0:
        logger.info(f"延迟 {delay} 秒后执行操作...")
        time.sleep(delay)
    
    # 1. 选择好友（使用Ctrl+F搜索）
    logger.info(f"步骤1: 使用 Ctrl+F 搜索并选择好友 '{friend_name}'")
    select_result = select_friend(friend_name)
    results.append({
        "step": 1,
        "action": "SELECTFRIEND",
        "success": select_result["success"],
        "message": select_result["message"]
    })
    
    if not select_result["success"]:
        return {
            "success": False,
            "message": f"选择好友失败，终止操作: {select_result['message']}",
            "results": results
        }
    
    time.sleep(0.5)
    
    # 2. 发送消息
    logger.info(f"步骤2: 发送消息 '{message_content[:50]}...'")
    send_success = send_text_message(message_content)
    results.append({
        "step": 2,
        "action": "SENDMESSAGE",
        "success": send_success,
        "message": f"发送消息: {message_content[:50]}{'...' if len(message_content) > 50 else ''}"
    })
    
    return {

        "success": select_result["success"] and send_success,
        "message": "操作完成" if (select_result["success"] and send_success) else "操作失败",
        "friend_name": friend_name,
        "message_content": message_content[:100],
        "results": results
    }


@app.post("/send_message")
async def send_message_endpoint(request: MessageRequest):
    """
    发送QQ消息（支持 [ACTION:SELECTFRIEND_SENDMESSAGE] 指令）
    """
    try:
        message = request.message
        delay = request.delay if request.delay is not None else 0
        
        logger.info(f"接收到请求: {message[:100]}...")
        
        # 解析 SELECTFRIEND_SENDMESSAGE 指令
        parsed = parse_selectfriend_sendmessage_action(message)
        
        if parsed.get("has_action"):
            friend_name = parsed.get("friend_name")
            message_content = parsed.get("message_content")
            
            # 检查解析错误
            if parsed.get("parse_error"):
                logger.warning(f"指令解析错误: {parsed.get('parse_error')}")
                return {
                    "success": False,
                    "message": f"指令解析失败: {parsed['parse_error']}",
                    "format_hint": "正确格式: [ACTION:SELECTFRIEND_SENDMESSAGE]好友名称|消息内容"
                }
            
            if not friend_name or not message_content:
                logger.warning("好友名称或消息内容为空")
                return {
                    "success": False,
                    "message": "指令解析失败",
                    "error": "好友名称或消息内容为空",
                    "format_hint": "正确格式: [ACTION:SELECTFRIEND_SENDMESSAGE]好友名称|消息内容"
                }
            
            logger.info(f"执行指令: 使用 Ctrl+F 搜索好友 '{friend_name}'，然后发送消息")
            result = execute_selectfriend_sendmessage(friend_name, message_content, delay)

            # 确保返回格式与前端期望一致
            if result.get("success"):
                logger.info(f"成功发送消息给好友 {friend_name}")
            else:
                logger.error(f"发送消息失败: {result.get('message', '未知错误')}")

            return result
        
        # 如果没有指令，直接发送消息到当前窗口
        logger.info("未检测到指令，直接发送消息到当前窗口")
        send_success = send_text_message(message)
        
        return {
            "success": send_success,
            "message": "消息发送成功" if send_success else "消息发送失败",
            "message_content": message[:100]
        }
        
    except Exception as e:
        logger.error(f"处理请求失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"处理失败: {str(e)}",
            "error": str(e)
        }


@app.post("/select_friend")
async def select_friend_endpoint(payload: dict = Body(...)):
    """选择QQ好友接口"""
    try:
        friend_name = payload.get("friend_name")
        
        if not friend_name:
            return {
                "success": False,
                "message": "未提供好友名称"
            }
        
        logger.info(f"选择好友: {friend_name}")
        result = select_friend(friend_name)
        
        return result
        
    except Exception as e:
        logger.error(f"选择好友请求失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"处理失败: {str(e)}"
        }


@app.post("/send_message_current")
async def send_message_to_current_chat(payload: dict = Body(...)):
    """向当前聊天窗口发送消息接口"""
    try:
        message = payload.get("message")
        
        if not message:
            return {
                "success": False,
                "message": "未提供消息内容"
            }
        
        logger.info(f"向当前窗口发送消息: {message[:50]}...")
        result = send_text_message(message)
        
        return {
            "success": result,
            "message": "消息发送成功" if result else "消息发送失败",
            "message_content": message[:100]
        }
        
    except Exception as e:
        logger.error(f"发送消息请求失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"处理失败: {str(e)}"
        }






if __name__ == "__main__":
    import uvicorn
    
    print("QQ消息发送服务 (端口: 8021)")
   
    
    # 检查依赖
    try:
        import win32con, win32api, win32gui, pyperclip
        print("✓ 依赖检查通过")
        print("  - pywin32: 已安装")
        print("  - pyperclip: 已安装")
        print("  - fastapi/uvicorn: 已安装")
    except ImportError as e:
        print(f"\n✗ 缺少依赖: {e}")
        print("请安装: pip install pywin32 pyperclip fastapi uvicorn")
        input("按回车键退出...")
        exit(1)
    

    
    # 启动服务器
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8021,
        log_level="info"
    )