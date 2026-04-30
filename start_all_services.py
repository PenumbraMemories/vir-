
import subprocess
import sys
import os
import time
import signal
from multiprocessing import Process

# 定义所有服务及其端口
SERVICES = [
    {"name": "tts_server", "file": "tts_server.py", "port": 8000},
    {"name": "qqchat", "file": "qqchat.py", "port": 8002},
    {"name": "single_website_service", "file": "single_website_service.py", "port": 8004},
    {"name": "action_collector", "file": "action_collector.py", "port": 8005},
    {"name": "action_executor", "file": "action_executor.py", "port": 8008},
    {"name": "waresoft_launcher", "file": "waresoft_launcher.py", "port": 8007},
    {"name": "log_monitor_service", "file": "log_monitor_service.py", "port": 8010},
    {"name": "screenshot_service", "file": "screenshot_service.py", "port": 8001},
    {"name": "windows_service", "file": "windows_service.py", "port": 8020},
    {"name": "stt_service", "file": "stt_service.py", "port": 8006},
]

def run_service(service):
    """运行单个服务"""
    try:
        # 获取当前脚本的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, "backend", service["file"])
        print(f"启动服务: {service['name']} (端口: {service['port']})...")
        print(f"脚本路径: {script_path}")
        subprocess.run([sys.executable, script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"服务 {service['name']} 启动失败: {e}")
    except KeyboardInterrupt:
        print(f"服务 {service['name']} 被中断")
    except Exception as e:
        print(f"服务 {service['name']} 运行出错: {e}")

def start_all_services():
    """启动所有服务"""
    processes = []

    try:
        print("正在启动所有服务...")
        print("-" * 50)

        # 为每个服务创建一个进程
        for service in SERVICES:
            p = Process(target=run_service, args=(service,))
            p.daemon = True  # 设置为守护进程，主进程退出时自动结束
            p.start()
            processes.append(p)
            time.sleep(1)  # 等待服务启动

        print("-" * 50)
        print(f"所有服务已启动，共 {len(processes)} 个服务")
        print("按 Ctrl+C 停止所有服务")

        # 保持主进程运行
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n正在停止所有服务...")
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join(timeout=5)
                if p.is_alive():
                    p.kill()
        print("所有服务已停止")

if __name__ == "__main__":
    start_all_services()
