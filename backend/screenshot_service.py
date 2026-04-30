#[ACTION:SCREENSHOT]
#已经改好了，不要再改动
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import pyautogui
import os

app = FastAPI()

# 添加CORS中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建截图保存目录（在桌面）
import pathlib
desktop = pathlib.Path.home() / "Desktop"
SCREENSHOT_DIR = os.path.join(desktop, "screenshots")
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

@app.post("/screenshot")
async def take_screenshot(payload: dict = Body(...)):
    """
    执行截图并返回截图信息

    参数:
        payload: 包含AI回答的字典
        {
            "message": "AI的回答内容"
        }

    返回:
        {
            "success": True/False,
            "message": "操作结果描述",
            "screenshot_path": "截图文件路径",
            "screenshot_url": "截图访问URL"
        }
    """
    try:
        message = payload.get("message", "")

        # 检查消息中是否包含截图指令
        if "[ACTION:SCREENSHOT]" not in message:
            return {
                "success": False,
                "message": "消息中不包含截图指令",
                "screenshot_path": None,
                "screenshot_url": None
            }

        # 执行截图
        screenshot = pyautogui.screenshot()

        # 使用固定文件名
        filename = "1.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)

        # 保存截图
        screenshot.save(filepath)

        # 返回结果
        return {
            "success": True,
            "message": "截图成功",
            "screenshot_path": filepath,
            "screenshot_url": f"http://localhost:8000/screenshots/{filename}"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"截图失败: {str(e)}",
            "screenshot_path": None,
            "screenshot_url": None
        }

@app.get("/screenshots/{filename}")
async def get_screenshot(filename: str):
    """
    获取截图文件

    参数:
        filename: 截图文件名

    返回:
        截图文件
    """
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return Response(content=f.read(), media_type="image/png")
    else:
        return Response(status_code=404, content="截图文件不存在")

if __name__ == "__main__":
    import uvicorn
    from fastapi.responses import Response
    uvicorn.run(app, host="0.0.0.0", port=8001)
