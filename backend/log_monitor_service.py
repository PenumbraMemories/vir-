
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
import re
import asyncio
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

# 存储调试面板日志的列表
debug_logs = []

class LogEntry(BaseModel):
    timestamp: str
    type: str
    message: str

def check_for_readlog_action(logs: list) -> Optional[str]:
    """
    检查日志中是否有[ACTION:READLOG]触发器

    Args:
        logs: 日志列表

    Returns:
        Optional[str]: 如果找到触发器，返回要发送的消息内容，否则返回None
    """
    for log in logs:
        if "[ACTION:READLOG]" in log.message:
            # 提取触发器后面的内容作为要发送的消息
            pattern = r'\[ACTION:READLOG\](.*?)$'
            match = re.search(pattern, log.message)
            if match:
                return match.group(1).strip()
            return ""
    return None

@app.post("/add_log")
async def add_log(log: LogEntry):
    """
    添加日志到调试面板

    Args:
        log: 日志条目

    Returns:
        Dict: 操作结果
    """
    debug_logs.append(log)

    # 检查是否有[ACTION:READLOG]触发器
    message_content = check_for_readlog_action(debug_logs)
    if message_content is not None:
        logger.info(f"检测到[ACTION:READLOG]触发器，准备发送消息: {message_content}")
        return {
            "success": True,
            "trigger_action": "READLOG",
            "message": message_content
        }

    return {
        "success": True,
        "trigger_action": None,
        "message": "日志已添加，未检测到触发器"
    }

@app.post("/get_debug_logs")
async def get_debug_logs():
    """
    获取调试面板的所有日志

    Returns:
        Dict: 包含所有日志的字典
    """
    return {
        "success": True,
        "logs": debug_logs
    }

@app.post("/clear_logs")
async def clear_logs():
    """
    清除所有日志

    Returns:
        Dict: 操作结果
    """
    debug_logs.clear()
    return {
        "success": True,
        "message": "日志已清除"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("启动日志监控服务...")
    uvicorn.run(app, host="0.0.0.0", port=8010)
