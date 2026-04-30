#[文字转语音]
#语音回答
#8000
from fastapi import FastAPI, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import edge_tts
import hashlib
from typing import Dict, Optional
from collections import defaultdict

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 缓存管理
_audio_cache: Dict[str, bytes] = {}
_cache_access_count: Dict[str, int] = defaultdict(int)
MAX_CACHE_SIZE = 200

def get_cached_audio(cache_key: str) -> Optional[bytes]:
    """获取缓存的音频数据"""
    if cache_key in _audio_cache:
        _cache_access_count[cache_key] += 1
        return _audio_cache[cache_key]
    return None

def set_cached_audio(cache_key: str, audio_data: bytes):
    """设置音频缓存，LRU淘汰"""
    if len(_audio_cache) >= MAX_CACHE_SIZE:
        min_key = min(_cache_access_count.items(), key=lambda x: x[1])[0]
        del _audio_cache[min_key]
        del _cache_access_count[min_key]
    _audio_cache[cache_key] = audio_data
    _cache_access_count[cache_key] = 1

def generate_cache_key(text: str, voice: str, pitch: str, rate: str) -> str:
    """生成缓存键"""
    return hashlib.md5(f"{text}|{voice}|{pitch}|{rate}".encode()).hexdigest()

async def generate_audio_stream(text: str, voice: str = "zh-CN-XiaoyiNeural", 
                                pitch: str = "+10Hz", rate: str = "-5%"):
    """生成音频流"""
    communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]

async def generate_audio_full(text: str, voice: str, pitch: str, rate: str) -> bytes:
    """生成完整音频数据"""
    audio_data = b""
    async for chunk in generate_audio_stream(text, voice, pitch, rate):
        audio_data += chunk
    return audio_data

def _get_params(payload: dict) -> tuple:
    """提取请求参数"""
    return (
        payload.get("text", "没有收到文字"),
        payload.get("voice", "zh-CN-XiaoyiNeural"),
        payload.get("pitch", "+10Hz"),
        payload.get("rate", "-5%")
    )

@app.post("/tts_dify")
async def tts_dify(payload: dict = Body(...)):
    """流式TTS接口"""
    text, voice, pitch, rate = _get_params(payload)
    cache_key = generate_cache_key(text, voice, pitch, rate)
    cached_audio = get_cached_audio(cache_key)

    if cached_audio:
        return Response(content=cached_audio, media_type="audio/mpeg")

    return StreamingResponse(
        generate_audio_stream(text, voice, pitch, rate),
        media_type="audio/mpeg"
    )

@app.post("/tts_cached")
async def tts_cached(payload: dict = Body(...)):
    """缓存TTS接口"""
    text, voice, pitch, rate = _get_params(payload)
    cache_key = generate_cache_key(text, voice, pitch, rate)
    cached_audio = get_cached_audio(cache_key)

    if cached_audio:
        return Response(content=cached_audio, media_type="audio/mpeg")

    audio_data = await generate_audio_full(text, voice, pitch, rate)
    set_cached_audio(cache_key, audio_data)
    return Response(content=audio_data, media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
