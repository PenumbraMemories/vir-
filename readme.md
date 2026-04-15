# dpchattt

一个基于 Electron + Vue.js 的智能桌面聊天应用，集成了 Dify AI 对话功能，并支持多种系统操作，如截图、发送QQ消息、打开网站、执行CMD命令等。

## 功能特点

### 核心功能

- 🤖 **智能对话**：集成 Dify AI，支持流式响应
- 🎤 **语音交互**：支持语音输入和语音输出
- 💾 **对话管理**：支持创建、切换、删除对话，历史记录本地存储
- 🌓 **主题切换**：支持深色/浅色主题
- 🪟 **窗口控制**：支持窗口置顶、侧边栏显示/隐藏

### 系统操作

- 📸 **屏幕截图**：快速截取屏幕并保存
- 💬 **QQ消息**：自动发送消息和文件到QQ好友
- 🌐 **网站打开**：自动打开指定网站
- ⌨️ **命令执行**：执行CMD命令并获取结果
- 📋 **窗口管理**：获取窗口列表、置顶指定窗口
- 🚀 **软件启动**：自动启动指定软件

### 调试功能

- 📝 **日志记录**：详细的操作日志记录
- 🔍 **调试面板**：实时查看系统日志

## 技术栈

### 前端

- Vue.js 3.2
- Electron 22.0
- Web Audio API
- Axios

### 后端

- Python 3.11
- FastAPI
- Uvicorn
- PyAutoGUI
- Win32API
- Faster-Whisper (语音识别)
- Librosa (音频处理)

## 项目结构

```
dpchattt/
├── backend/                 # 后端服务目录
│   ├── action_executor.py    # 命令执行服务
│   ├── log_monitor_service.py # 日志监控服务
│   ├── qqchat.py           # QQ消息服务
│   ├── screenshot_service.py # 截图服务
│   ├── single_website_service.py # 网站打开服务
│   ├── stt_service.py      # 语音识别服务
│   ├── tts_server.py       # 语音合成服务
│   ├── waresoft_launcher.py # 软件启动服务
│   └── windows_service.py  # Windows服务
├── dpchatt/               # 前端应用目录
│   ├── public/            # 静态资源
│   ├── src/
│   │   ├── components/    # Vue组件
│   │   ├── assets/        # 资源文件
│   │   ├── App.vue        # 主应用组件
│   │   ├── background.js   # Electron主进程
│   │   └── main.js       # 应用入口
│   ├── package.json       # 前端依赖配置
│   └── vue.config.js     # Vue配置
├── LICENSE               # 许可证文件
└── README.md            # 项目说明文档
```

## 安装指南

### 环境要求

- Windows 操作系统
- Python 3.11+
- Node.js 14+
- NVIDIA GPU (用于语音识别加速，可选)

### 前端安装

1. 克隆项目

```bash
git clone <repository-url>
cd dpchattt/dpchatt
```

2. 安装依赖

```bash
npm install 如果网络环境出现问题先设置镜像set ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
```

3. 启动开发服务器

```bash
npm run electron:serve
```

4. 构建生产版本

```bash
npm run electron:build
```

### 后端安装

1. 安装Python依赖

```bash
cd backend
pip install fastapi uvicorn pyautogui win32api faster-whisper librosa
```

2. 启动各个服务

```bash
# TTS服务 (端口8000)
python tts_server.py

# 截图服务 (端口8001)
python screenshot_service.py

# QQ消息服务 (端口8002)
python qqchat.py

# 日志监控服务 (端口8003)
python log_monitor_service.py

# 网站打开服务 (端口8004)
python single_website_service.py

# Windows服务 (端口8005)
python windows_service.py

# 语音识别服务 (端口8006)
python stt_service.py

# 软件启动服务 (端口8007)
python waresoft_launcher.py

# 命令执行服务 (端口8008)
python action_executor.py
```

## 使用说明

### 基本使用

1. **发送消息**

   - 在输入框中输入消息
   - 点击发送按钮或按Enter键
   - AI将返回流式响应
2. **语音输入（很慢）**

   - 点击"开始录音"按钮
   - 说出您的消息
   - 点击"停止录音"按钮
   - 系统将自动识别语音并填充到输入框
3. **语音输出（很慢）**

   - 在侧边栏的TTS控制区域
   - 开启"开启语音回答"开关
   - AI回复将自动朗读

### 系统操作

AI可以通过特定的指令标记执行系统操作：

- `[ACTION:SCREENSHOT]` - 执行屏幕截图
- `[ACTION:SELECTFRIEND]好友名[ACTION:SENDMESSAGE]消息内容` - 发送QQ消息
- `[ACTION:SELECTFRIEND]好友名[ACTION:SENDFILE]文件路径` - 发送QQ文件
- `[ACTION:OPENWEBSITE]URL` - 打开网站
- `[ACTION:NOWWINDOWS]` - 获取窗口列表
- `[ACTION:TOPWINDOWS]窗口标题` - 置顶窗口
- `[ACTION:OPENSOFTWARE]` - 启动软件
- `[ACTION:OPENCMD]命令` - 执行CMD命令
- `[ACTION:READLOG]` - 读取调试日志

### 调试面板

1. 点击顶部工具栏的调试按钮
2. 右侧将显示调试面板
3. 查看系统操作日志
4. 点击"清除日志"按钮清除所有日志

## 配置说明

### Dify API配置

在 `dpchatt/src/App.vue` 中配置Dify API：

```javascript
difyApiKey: 'your-api-key',
difyApiUrl: 'https://api.dify.ai/v1',
```

### 服务端口配置

各服务默认端口：

- 8000: TTS 服务
- 8001: 截图服务
- 8002: QQ消息服务
- 8003: 日志监控服务
- 8004: 网站打开服务
- 8005: Windows服务
- 8006: 语音识别服务
- 8007: 软件启动服务
- 8008: 命令执行服务

## 开发指南

### 添加新的系统操作

1. 在后端创建新的服务文件
2. 实现相应的API接口
3. 在前端 `App.vue` 中添加调用方法
4. 添加对应的指令标记处理逻辑

### 修改UI样式

主要样式文件在 `App.vue` 的 `<style>` 部分，支持深色/浅色主题切换。

## 常见问题

### Q: 提问失败建立新对话会有一段长卡顿？

A: 这是一个已知问题，计划在后续版本中优化。

### Q: 执行多个指令时无法按顺序执行？

A: 目前指令是并行执行的，我们正在优化为顺序执行。

### Q: 截图后立马发送会找不到文件？

A: 这是由于文件保存和发送之间的时间差导致的，我们正在优化文件处理逻辑。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

请查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请提交 Issue。
