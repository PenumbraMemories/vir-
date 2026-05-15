# Dify API代理服务
from fastapi import FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import httpx
import json

# 配置日志
logging.basicConfig(level=logging.INFO,
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

# Dify API配置
DIFY_API_BASE_URL = "https://api.dify.ai/v1"
DIFY_API_KEY = "请输入你的dify agent api"

@app.post("/chat-messages")
async def chat_messages(request: Request, payload: dict = Body(...)):
    """
    代理Dify的chat-messages API
    """
    try:
        logger.info(f"========== Dify API请求开始 ==========")
        logger.info(f"请求URL: {DIFY_API_BASE_URL}/chat-messages")
        logger.info(f"请求体: {json.dumps(payload, ensure_ascii=False)}")

        # 使用配置的API密钥
        api_key = DIFY_API_KEY
        
        logger.info(f"使用配置的API密钥: {api_key[:20]}...")

        # 准备发送到Dify API的请求
        dify_payload = {
            "inputs": payload.get("inputs", {}),
            "query": payload.get("query", ""),
            "response_mode": payload.get("response_mode", "streaming"),
            "conversation_id": payload.get("conversation_id", ""),
            "user": payload.get("user", ""),
        }

        # 使用httpx发送请求到Dify API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{DIFY_API_BASE_URL}/chat-messages",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                },
                json=dify_payload
            )

            logger.info(f"Dify API响应状态码: {response.status_code}")

            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Dify API错误响应: {error_text}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_text
                }

            logger.info(f"========== Dify API请求成功 ==========")

            # 返回流式响应
            from fastapi.responses import StreamingResponse
            async def generate():
                async for chunk in response.aiter_bytes():
                    yield chunk

            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )

    except Exception as e:
        logger.error(f"========== Dify API请求失败 ==========")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}", exc_info=True)
        logger.error(f"========== 请求结束 ==========")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
