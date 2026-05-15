# 8023-对已存图像库进行图像识别与点击服务
# 专注于处理[ACTION:CLICKBUTTON]指令

import cv2
import numpy as np
import pyautogui
import os
import re
import logging
import uvicorn
from typing import Dict, List
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

# 程序防故障机制：如果鼠标失控，将鼠标猛甩到屏幕左上角即可强制暂停
pyautogui.FAILSAFE = True

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="图像识别点击服务", description="专注于处理CLICKBUTTON指令")

# 添加CORS中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
logger.info(f"当前工作目录: {current_dir}")

# 定义图片文件夹路径
folder_kugou = os.path.join(current_dir, "酷狗")
folder_qq = os.path.join(current_dir, "QQ")

# 确保文件夹存在
if not os.path.exists(folder_kugou):
    logger.warning(f"酷狗文件夹不存在: {folder_kugou}")
    # 尝试使用上级目录
    parent_dir = os.path.dirname(current_dir)
    folder_kugou = os.path.join(parent_dir, "酷狗")
    folder_qq = os.path.join(parent_dir, "QQ")

logger.info(f"酷狗文件夹路径: {folder_kugou}")
logger.info(f"QQ文件夹路径: {folder_qq}")

# 定义图片路径字典
images = {
    "下一首": os.path.join(folder_kugou, "下一首.png"),
    "上一首": os.path.join(folder_kugou, "上一首.png"),
    "暂停": os.path.join(folder_kugou, "暂停.png"),
    "播放": os.path.join(folder_kugou, "播放.png"),
    "搜索好友": os.path.join(folder_qq, "搜索好友.png"),
    "发送": os.path.join(folder_qq, "发送.png"),
    "最小化": os.path.join(folder_kugou, "最小化.png"),
    "关闭": os.path.join(folder_kugou, "关闭.png"),
}

# 检查图片文件是否存在
available_buttons = []
missing_buttons = []

for name, path in images.items():
    if os.path.exists(path):
        logger.info(f"✓ 找到图片: {name} -> {path}")
        available_buttons.append(name)
    else:
        logger.warning(f"✗ 图片不存在: {name} -> {path}")
        missing_buttons.append(name)

def parse_clickbutton_actions(message: str) -> List[str]:
    """
    解析AI回复中的所有CLICKBUTTON操作标记
    
    Args:
        message: AI的回答内容
        
    Returns:
        按钮名称列表
    """
    # 匹配 [ACTION:CLICKBUTTON]按钮名称 格式
    pattern = r'\[ACTION:CLICKBUTTON\](.*?)(?=\[ACTION|$)'
    matches = re.findall(pattern, message, re.DOTALL)
    
    # 清理按钮名称（去除前后空格和换行）
    buttons = [match.strip() for match in matches if match.strip()]
    
    return buttons

def find_and_click_button(button_name: str, threshold: float = 0.8) -> Dict:
    """
    在屏幕上查找并点击指定按钮
    
    Args:
        button_name: 按钮名称（必须存在于images字典中）
        threshold: 匹配阈值（0-1），默认0.8
        
    Returns:
        操作结果字典
    """
    try:
        button_name = button_name.strip()
        
        # 检查按钮是否在图片库中
        if button_name not in images:
            logger.error(f"未找到按钮配置: {button_name}")
            return {
                "success": False,
                "message": f"未找到按钮配置: '{button_name}'，可用的按钮: {available_buttons}",
                "button": button_name,
                "available_buttons": available_buttons
            }

        template_path = images[button_name]
        logger.info(f"尝试查找并点击: {button_name} ({template_path})")
        
        # 检查图片文件是否存在
        if not os.path.exists(template_path):
            logger.error(f"图片文件不存在: {template_path}")
            return {
                "success": False,
                "message": f"图片文件不存在: {template_path}",
                "button": button_name
            }
        
        # 使用 cv2.imdecode 处理中文路径
        with open(template_path, 'rb') as f:
            img_data = np.frombuffer(f.read(), dtype=np.uint8)
            template = cv2.imdecode(img_data, cv2.IMREAD_GRAYSCALE)
        
        if template is None:
            logger.error(f"无法加载图片: {template_path}")
            return {
                "success": False,
                "message": f"无法加载图片: {template_path}",
                "button": button_name
            }

        h, w = template.shape[:2]

        # 截取屏幕
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)

        # 模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # 计算点击位置（按钮中心）
            x = max_loc[0] + w // 2
            y = max_loc[1] + h // 2

            # 执行点击
            pyautogui.click(x, y)
            logger.info(f"✓ 成功点击 '{button_name}'，位置: ({x}, {y})，置信度: {max_val:.2f}")
            
            return {
                "success": True,
                "message": f"成功点击 '{button_name}' 按钮",
                "button": button_name,
                "position": {"x": x, "y": y},
                "confidence": float(max_val),
                "threshold_used": threshold
            }
        else:
            logger.warning(f"✗ 未找到 '{button_name}'，最佳匹配置信度: {max_val:.2f} (需要 >= {threshold})")
            return {
                "success": False,
                "message": f"未找到 '{button_name}' 按钮，最佳匹配置信度: {max_val:.2f} (需要 >= {threshold})",
                "button": button_name,
                "confidence": float(max_val),
                "threshold_required": threshold
            }
            
    except Exception as e:
        logger.error(f"点击按钮 '{button_name}' 时发生错误: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"点击按钮时发生错误: {str(e)}",
            "button": button_name,
            "error": str(e)
        }

def process_clickbutton_actions(message: str, threshold: float = 0.8) -> Dict:
    """
    处理AI消息中的所有CLICKBUTTON指令
    
    Args:
        message: AI的回答内容，可能包含多个[ACTION:CLICKBUTTON]指令
        threshold: 图片匹配阈值
        
    Returns:
        处理结果汇总
    """
    try:
        # 解析所有CLICKBUTTON指令
        buttons = parse_clickbutton_actions(message)
        
        if not buttons:
            logger.info("未检测到CLICKBUTTON指令")
            return {
                "success": False,
                "message": "未检测到[ACTION:CLICKBUTTON]指令",
                "results": [],
                "buttons_found": []
            }
        
        logger.info(f"检测到 {len(buttons)} 个CLICKBUTTON指令: {buttons}")
        
        # 依次执行每个按钮点击
        results = []
        all_success = True
        
        for idx, button_name in enumerate(buttons, 1):
            logger.info(f"执行第 {idx}/{len(buttons)} 个指令: {button_name}")
            result = find_and_click_button(button_name, threshold)
            results.append(result)
            
            if not result["success"]:
                all_success = False
                
            # 在连续点击之间添加短暂延迟，避免操作过快
            if idx < len(buttons):
                pyautogui.sleep(0.5)
        
        # 统计结果
        success_count = sum(1 for r in results if r["success"])
        fail_count = len(results) - success_count
        
        return {
            "success": all_success and success_count > 0,
            "message": f"执行完成: 成功 {success_count} 个，失败 {fail_count} 个",
            "results": results,
            "summary": {
                "total": len(buttons),
                "success": success_count,
                "failed": fail_count,
                "buttons": buttons
            }
        }
        
    except Exception as e:
        logger.error(f"处理CLICKBUTTON指令时发生错误: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"处理失败: {str(e)}",
            "results": [],
            "error": str(e)
        }

@app.post("/process_clickbutton")
async def process_clickbutton_endpoint(payload: dict = Body(...)):
    """
    处理CLICKBUTTON指令端点
    
    请求格式:
    {
        "message": "AI的回答内容，包含[ACTION:CLICKBUTTON]指令",
        "threshold": 0.8  // 可选，图片匹配阈值，默认0.8
    }
    
    支持的指令格式:
    - 单个指令: "[ACTION:CLICKBUTTON]下一首"
    - 多个指令: "[ACTION:CLICKBUTTON]下一首[ACTION:CLICKBUTTON]暂停"
    - 带文本的混合: "我需要点击[ACTION:CLICKBUTTON]播放按钮来开始音乐"
    
    响应格式:
    {
        "success": true/false,
        "message": "操作结果描述",
        "results": [...],  // 每个按钮的详细点击结果
        "summary": {       // 汇总信息
            "total": 2,
            "success": 2,
            "failed": 0,
            "buttons": ["下一首", "暂停"]
        }
    }
    """
    try:
        # 获取参数
        message = payload.get("message", "")
        threshold = payload.get("threshold", 0.8)
        
        # 验证参数
        if not message:
            return {
                "success": False,
                "message": "未提供消息内容（message参数）",
                "results": [],
                "error": "Missing message parameter"
            }
        
        # 验证阈值
        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
            logger.warning(f"无效的阈值: {threshold}，使用默认值0.8")
            threshold = 0.8
        
        # 处理CLICKBUTTON指令
        result = process_clickbutton_actions(message, threshold)
        return result
        
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"处理失败: {str(e)}",
            "results": [],
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "service": "image-recognition-click-service",
        "port": 8023,
        "description": "专注于处理[ACTION:CLICKBUTTON]指令的图像识别点击服务",
        "supported_actions": ["CLICKBUTTON"],
        "available_buttons": available_buttons,
        "missing_buttons": missing_buttons,
        "total_buttons": len(available_buttons)
    }

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("启动图像识别点击服务...")
    logger.info("端口: 8023")
    logger.info("服务类型: 专注于 [ACTION:CLICKBUTTON] 指令")
    logger.info("唯一端点: POST /process_clickbutton")
    logger.info("=" * 60)
    logger.info("可用的按钮:")
    for name in available_buttons:
        logger.info(f"  ✓ {name}: {images[name]}")
    if missing_buttons:
        logger.warning(f"\n缺失的按钮图片 ({len(missing_buttons)}个):")
        for name in missing_buttons:
            logger.warning(f"  ✗ {name}: {images[name]}")
    logger.info("=" * 60)
    logger.info("使用示例:")
    logger.info('  POST http://localhost:8023/process_clickbutton')
    logger.info('  {')
    logger.info('    "message": "[ACTION:CLICKBUTTON]下一首[ACTION:CLICKBUTTON]暂停"')
    logger.info('  }')
    logger.info("=" * 60)
    
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8023)
    uvicorn.run(app, host="0.0.0.0", port=8023)