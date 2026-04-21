#[ACTION:OPENSOFTWARE]
import subprocess
import os
import json
import time
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 添加CORS中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QQLauncher:
    def __init__(self):
        self.qq_path = r"D:\QQ\QQ.exe"
        self.process = None
        self.running_processes = {}  # 存储所有运行的软件进程
        
    def start_qq(self):
        """启动QQ.exe"""
        try:
            if not os.path.exists(self.qq_path):
                return {"status": "error", "message": f"QQ.exe not found at {self.qq_path}"}
            
            # 检查是否已经在运行
            if self.process and self.process.poll() is None:
                return {"status": "error", "message": "QQ is already running"}
            
            # 启动QQ进程，不重定向输入输出以避免阻塞
            self.process = subprocess.Popen(
                [self.qq_path],
                shell=False
            )
            
            # 等待进程启动
            time.sleep(2)
            
            if self.process.poll() is None:
                return {"status": "success", "message": "QQ started successfully", "pid": self.process.pid}
            else:
                return {"status": "error", "message": "QQ failed to start"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def start_software(self, software_path):
        """启动指定路径的软件"""
        try:
            if not os.path.exists(software_path):
                return {"status": "error", "message": f"Software not found at {software_path}"}

            # 检查是否已经在运行
            software_name = os.path.basename(software_path)
            if software_name in self.running_processes and self.running_processes[software_name].poll() is None:
                return {"status": "error", "message": f"{software_name} is already running"}

            # 启动软件进程，不重定向输入输出以避免阻塞
            process = subprocess.Popen(
                [software_path],
                shell=False
            )

            # 保存进程引用
            self.running_processes[software_name] = process

            # 等待进程启动
            time.sleep(2)

            if process.poll() is None:
                return {"status": "success", "message": f"{software_name} started successfully", "pid": process.pid}
            else:
                return {"status": "error", "message": f"{software_name} failed to start"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def stop_qq(self):
        """停止QQ进程"""
        try:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                self.process.wait(timeout=5)
                return {"status": "success", "message": "QQ stopped successfully"}
            return {"status": "error", "message": "QQ is not running"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_status(self):
        """获取QQ运行状态"""
        try:
            if self.process and self.process.poll() is None:
                return {"status": "running", "pid": self.process.pid}
            return {"status": "stopped"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# 创建全局实例
qq_launcher = QQLauncher()

@app.post("/api/qq/start")
async def start_qq():
    """启动QQ的API接口"""
    result = qq_launcher.start_qq()
    return result

@app.post("/api/qq/stop")
async def stop_qq():
    """停止QQ的API接口"""
    result = qq_launcher.stop_qq()
    return result

@app.get("/api/qq/status")
async def get_qq_status():
    """获取QQ状态的API接口"""
    result = qq_launcher.get_status()
    return result

@app.post("/api/qq/restart")
async def restart_qq():
    """重启QQ的API接口"""
    # 先停止
    stop_result = qq_launcher.stop_qq()
    if stop_result.get('status') == 'success' or stop_result.get('status') == 'stopped':
        # 等待一下
        time.sleep(1)
        # 再启动
        start_result = qq_launcher.start_qq()
        return start_result
    return stop_result

@app.post("/api/qq/check_and_start")
async def check_and_start_qq(payload: dict = Body(...)):
    """检查AI回复并根据[ACTION:OPENSOFTWARE]后面的路径启动对应软件，支持同时启动多个软件"""
    try:
        message = payload.get('message', '')

        # 检查消息中是否包含 [ACTION:OPENSOFTWARE]
        if '[ACTION:OPENSOFTWARE]' in message:
            # 提取 [ACTION:OPENSOFTWARE] 后面的 exe 路径
            import re
            # 修改正则表达式以匹配包含空格和特殊字符的完整路径
            pattern = r'\[ACTION:OPENSOFTWARE\]\s*([^\[\]]+\.exe)'
            matches = re.findall(pattern, message, re.IGNORECASE)

            if not matches:
                return {
                    "status": "error",
                    "message": "Found [ACTION:OPENSOFTWARE] but no valid exe path was provided"
                }

            # 启动所有匹配的软件
            results = []
            success_count = 0
            for software_path in matches:
                start_result = qq_launcher.start_software(software_path)
                results.append({
                    "software_path": software_path,
                    "status": start_result.get('status'),
                    "message": start_result.get('message')
                })
                if start_result.get('status') == 'success':
                    success_count += 1

            if success_count > 0:
                return {
                    "status": "success",
                    "message": f"Successfully started {success_count} out of {len(matches)} software(s)",
                    "results": results
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to start any software",
                    "results": results
                }
        else:
            return {
                "status": "no_action",
                "message": "No [ACTION:OPENSOFTWARE] detected in the message"
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "qq_launcher"}

@app.get("/")
async def index():
    """根路径，显示服务信息"""
    return {
        "service": "QQ Launcher Service",
        "version": "1.0.0",
        "endpoints": {
            "start_qq": "POST /api/qq/start",
            "stop_qq": "POST /api/qq/stop",
            "status": "GET /api/qq/status",
            "restart": "POST /api/qq/restart",
            "check_and_start": "POST /api/qq/check_and_start",
            "health": "GET /health"
        }
    }

def main():
    """主函数，启动HTTP服务"""
    # 从环境变量获取端口，默认8007
    port = int(os.environ.get('QQ_LAUNCHER_PORT', 8007))
    host = os.environ.get('QQ_LAUNCHER_HOST', '0.0.0.0')
    
    print(f"Starting QQ Launcher Service on {host}:{port}")
    print(f"QQ path: {qq_launcher.qq_path}")
    
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()