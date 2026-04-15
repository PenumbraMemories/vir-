from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import webbrowser
import re
from typing import List

app = FastAPI()

# 添加CORS中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_urls_from_text(text: str) -> List[str]:
    """
    从文本中提取所有URL

    参数:
        text: 要搜索的文本

    返回:
        包含所有找到的URL的列表
    """
    # 匹配http://或https://开头的URL
    url_pattern = r'https?://[^\s)\]"]+'
    urls = re.findall(url_pattern, text)
    return urls

@app.post("/open_website_from_message")
async def open_website_from_message(payload: dict = Body(...)):
    """
    从单条消息中提取并打开网址

    参数:
        payload: 包含消息内容的字典
        {
            "message": "消息内容，可能包含网址"
        }

    返回:
        {
            "success": True/False,
            "message": "操作结果描述",
            "urls": ["打开的URL1", "打开的URL2"],
            "count": 打开的URL数量
        }
    """
    try:
        message = payload.get("message", "")

        if not message:
            return {
                "success": False,
                "message": "未提供消息内容",
                "urls": [],
                "count": 0
            }

        # 从消息中提取所有URL
        urls = extract_urls_from_text(message)

        # 去重
        unique_urls = list(set(urls))

        if not unique_urls:
            return {
                "success": False,
                "message": "消息中未找到任何网址",
                "urls": [],
                "count": 0
            }

        # 打开所有找到的网址
        opened_urls = []
        for url in unique_urls:
            try:
                webbrowser.open(url)
                opened_urls.append(url)
            except Exception as e:
                print(f"无法打开网址 {url}: {str(e)}")

        return {
            "success": True,
            "message": f"成功打开 {len(opened_urls)} 个网址",
            "urls": opened_urls,
            "count": len(opened_urls)
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"处理失败: {str(e)}",
            "urls": [],
            "count": 0
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
