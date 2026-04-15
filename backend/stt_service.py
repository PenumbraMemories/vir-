import os
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from datetime import datetime
from faster_whisper import WhisperModel

# --- 1. 显卡环境初始化 (确保 4060 能被调用) ---
nvidia_dir = r"C:\Users\21957\AppData\Local\Programs\Python\Python311\Lib\site-packages\nvidia"
for sub in ["cublas/bin", "cudnn/bin"]:
    path = os.path.join(nvidia_dir, sub.replace("/", os.sep))
    if os.path.exists(path):
        os.environ["PATH"] += os.pathsep + path
        os.add_dll_directory(path)

# --- 2. 模型配置 ---
# 使用 large-v3-turbo + float16，这是 4060 的黄金组合
model_size = "large-v3-turbo"
device = "cuda"  # 强制使用显卡
compute_type = "float16"

print(f"正在加载模型 {model_size} 到 GPU...")
model = WhisperModel(model_size, device=device, compute_type=compute_type)
print(f"模型 {model_size} 加载完成!")
print("=" * 60)

# --- 3. 创建FastAPI应用 ---
app = FastAPI()

# 添加CORS中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    接收音频文件并进行语音识别

    参数:
        file: 上传的音频文件

    返回:
        {
            "success": True/False,
            "text": "识别出的文本",
            "duration": 音频时长(秒)
        }
    """
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 收到语音识别请求")
    print(f"文件名: {file.filename}, 内容类型: {file.content_type}")
    
    try:
        # 读取上传的音频文件
        audio_bytes = await file.read()
        print(f"接收到 {len(audio_bytes)} 字节的音频数据")
        
        # 使用librosa加载音频文件，自动处理采样率转换
        import librosa
        import io
        
        # 将字节流转换为文件对象
        audio_file = io.BytesIO(audio_bytes)
        
        # 使用librosa加载音频，自动转换为16kHz采样率
        audio_array, sr = librosa.load(audio_file, sr=16000)
        
        # 确保音频数据是float32类型
        audio_array = audio_array.astype(np.float32)
        
        print(f"音频数组形状: {audio_array.shape}")
        print(f"采样率: {sr} Hz")

        # 计算音频时长
        duration = len(audio_array) / 16000  # 假设采样率为16kHz
        print(f"音频时长: {duration:.2f} 秒")

        # 执行转写
        print("开始语音识别...")
        segments, info = model.transcribe(
            audio_array,
            language="zh",
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        print(f"识别信息: 检测到的语言='{info.language}'，语言概率={info.language_probability:.2f}")

        # 提取所有文本
        text_segments = []
        for segment in segments:
            if segment.text.strip():
                print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
                text_segments.append(segment.text)
        
        text = " ".join(text_segments)

        print(f"\n识别结果: {text}")
        print("-" * 60)

        return {
            "success": True,
            "text": text,
            "duration": duration
        }
    except Exception as e:
        print(f"\n识别失败: {str(e)}")
        print("-" * 60)
        return {
            "success": False,
            "text": "",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("STT服务启动中...")
    print(f"服务地址: http://0.0.0.0:8006")
    print("API端点: /transcribe")
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8006)
