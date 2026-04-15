
from fastapi import FastAPI, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import edge_tts
import hashlib
from typing import Dict
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import time

app = FastAPI()

# 添加CORS中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 线程池用于处理TTS请求
executor = ThreadPoolExecutor(max_workers=4)

# 音频缓存字典
_audio_cache: Dict[str, bytes] = {}
# 缓存访问计数，用于LRU淘汰
_cache_access_count: Dict[str, int] = defaultdict(int)
# 缓存创建时间
_cache_create_time: Dict[str, float] = {}
# 最大缓存条目数
MAX_CACHE_SIZE = 200

def get_cached_audio(cache_key: str) -> bytes:
    """获取缓存的音频数据"""
    if cache_key in _audio_cache:
        _cache_access_count[cache_key] += 1
        return _audio_cache[cache_key]
    return None

def set_cached_audio(cache_key: str, audio_data: bytes):
    """设置音频缓存"""
    # 如果缓存已满，移除最少使用的条目
    if len(_audio_cache) >= MAX_CACHE_SIZE:
        # 找到访问次数最少的键
        min_access_key = min(_cache_access_count.items(), key=lambda x: x[1])[0]
        del _audio_cache[min_access_key]
        del _cache_access_count[min_access_key]
        del _cache_create_time[min_access_key]

    _audio_cache[cache_key] = audio_data
    _cache_access_count[cache_key] = 1
    _cache_create_time[cache_key] = time.time()

def generate_cache_key(text: str, voice: str, pitch: str, rate: str) -> str:
    """生成缓存键"""
    content = f"{text}|{voice}|{pitch}|{rate}"
    return hashlib.md5(content.encode()).hexdigest()

async def generate_audio_stream(text: str, voice: str = "zh-CN-XiaoyiNeural", 
                                pitch: str = "+10Hz", rate: str = "-5%"):
    """生成音频流，使用线程池处理"""
    communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)

    async def stream_generator():
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]

    return stream_generator()

async def generate_audio_full(text: str, voice: str = "zh-CN-XiaoyiNeural",
                             pitch: str = "+10Hz", rate: str = "-5%") -> bytes:
    """生成完整音频数据"""
    communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)

    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]

    return audio_data

@app.post("/tts_dify")
async def tts_dify(payload: dict = Body(...)):
    text = payload.get("text", "没有收到文字")
    voice = payload.get("voice", "zh-CN-XiaoyiNeural")
    pitch = payload.get("pitch", "+10Hz")
    rate = payload.get("rate", "-5%")

    # 检查缓存
    cache_key = generate_cache_key(text, voice, pitch, rate)
    cached_audio = get_cached_audio(cache_key)

    if cached_audio:
        return Response(content=cached_audio, media_type="audio/mpeg")

    # 使用流式传输，减少首字节时间
    return StreamingResponse(
        await generate_audio_stream(text, voice, pitch, rate),
        media_type="audio/mpeg"
    )

@app.post("/tts_cached")
async def tts_cached(payload: dict = Body(...)):
    """使用缓存的TTS接口，适合重复文本场景"""
    text = payload.get("text", "没有收到文字")
    voice = payload.get("voice", "zh-CN-XiaoyiNeural")
    pitch = payload.get("pitch", "+10Hz")
    rate = payload.get("rate", "-5%")

    # 检查缓存
    cache_key = generate_cache_key(text, voice, pitch, rate)
    cached_audio = get_cached_audio(cache_key)

    if cached_audio:
        return Response(content=cached_audio, media_type="audio/mpeg")

    # 生成完整音频并缓存
    audio_data = await generate_audio_full(text, voice, pitch, rate)

    # 缓存音频数据
    set_cached_audio(cache_key, audio_data)

    return Response(content=audio_data, media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
