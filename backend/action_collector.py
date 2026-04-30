#收集，决定执行顺序
#已经修改完成，不要再改动
#8005
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
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

def parse_ai_actions(message: str) -> Dict:
    """
    解析AI回复中的操作标记

    Args:
        message: AI返回的消息内容

    Returns:
        Dict: 包含解析出的操作和参数
    """
    actions = {
        "SENDMESSAGE": None,
        "SELECTFRIEND": None,
        "NOWWINDOWS": False,
        "SCREENSHOT": False,
        "TOPWINDOWS": None
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

def collect_actions(message: str) -> Dict:
    """
    收集指令并决定执行顺序

    Args:
        message: AI返回的消息内容

    Returns:
        Dict: 包含收集到的指令和执行顺序
    """
    # 解析AI消息中的操作
    actions = parse_ai_actions(message)

    # 定义指令的执行顺序
    execution_order = []

    # 收集需要立即执行的指令（并行执行）
    parallel_actions = []

    # 处理发送QQ消息操作（立即执行）
    if actions["SELECTFRIEND"] and actions["SENDMESSAGE"]:
        logger.info("检测到发送QQ消息操作")
        parallel_actions.append({
            "action_type": "SENDMESSAGE",
            "params": {
                "friend": actions["SELECTFRIEND"],
                "content": actions["SENDMESSAGE"]
            },
            "execution": "parallel"
        })

    # 收集需要串行执行的指令
    serial_actions = []

    # 收集获取窗口操作
    if actions["NOWWINDOWS"]:
        logger.info("检测到获取窗口操作")
        serial_actions.append({
            "action_type": "NOWWINDOWS",
            "params": {},
            "execution": "serial"
        })

    # 收集截图操作
    if actions["SCREENSHOT"]:
        logger.info("检测到截图操作")
        serial_actions.append({
            "action_type": "SCREENSHOT",
            "params": {"message": message},
            "execution": "serial"
        })

    # 收集置顶窗口操作
    if actions["TOPWINDOWS"]:
        logger.info(f"检测到置顶窗口操作: {actions['TOPWINDOWS']}")
        serial_actions.append({
            "action_type": "TOPWINDOWS",
            "params": {"window_title": actions["TOPWINDOWS"]},
            "execution": "serial"
        })

    # 构建执行顺序
    execution_order = {
        "parallel": parallel_actions,
        "serial": serial_actions
    }

    # 返回结果
    return {
        "success": True,
        "message": "指令收集完成",
        "actions": execution_order,
        "total_actions": len(parallel_actions) + len(serial_actions)
    }

@app.post("/collect_actions")
async def collect_actions_endpoint(payload: dict = Body(...)):
    """
    收集指令并决定执行顺序的接口

    参数:
        payload: 包含AI回答的字典
        {
            "message": "AI的回答内容，可能包含[ACTION:SELECTFRIEND]和[ACTION:SENDMESSAGE]等标记"
        }

    返回:
        {
            "success": True/False,
            "message": "操作结果描述",
            "actions": {
                "parallel": [
                    {
                        "action_type": "操作类型",
                        "params": {...},
                        "execution": "parallel"
                    },
                    ...
                ],
                "serial": [
                    {
                        "action_type": "操作类型",
                        "params": {...},
                        "execution": "serial"
                    },
                    ...
                ]
            },
            "total_actions": 指令总数
        }
    """
    try:
        message = payload.get("message", "")
        logger.debug(f"接收到的消息: {message}")

        if not message:
            return {
                "success": False,
                "message": "未提供消息内容",
                "actions": {
                    "parallel": [],
                    "serial": []
                },
                "total_actions": 0
            }

        # 收集指令并决定执行顺序
        result = collect_actions(message)

        return result

    except Exception as e:
        logger.error(f"收集指令时发生错误: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"收集指令失败: {str(e)}",
            "actions": {
                "parallel": [],
                "serial": []
            },
            "total_actions": 0
        }

if __name__ == "__main__":
    import uvicorn
    logger.info("启动指令收集服务...")
    uvicorn.run(app, host="0.0.0.0", port=8005)
