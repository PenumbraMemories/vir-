# dpchattttt 项目说明文档

## 项目简介

dpchattttt 是一个集成了多种AI功能的智能对话系统，支持语音交互、文本转语音、语音转文字、自动执行系统操作等功能。该项目通过前后端分离的架构，提供了一个功能强大且用户友好的智能对话平台。

### 主要功能

1. **智能对话系统**：支持与AI进行文本对话，保存和管理对话历史
2. **语音交互**：
   - 文字转语音（TTS）：使用Edge TTS将文字转换为语音
   - 支持自动播放和手动播放两种模式
3. **系统操作自动化**：
   - 自动发送QQ消息
   - 自动打开网站
   - 自动打开软件
   - 执行系统命令
   - 窗口管理（置顶、获取窗口列表）
   - 屏幕截图
4. **日志监控**：实时监控系统日志并显示在调试面板中

## 项目结构

```
dpchattttt/
├── backend/                      # 后端服务目录
│   ├── action_collector.py       # 动作收集器，决定指令执行顺序
│   ├── action_executor.py        # 动作执行器，执行解析出的操作
│   ├── log_monitor_service.py    # 日志监控服务
│   ├── qqchat.py                # QQ聊天自动化服务
│   ├── screenshot_service.py    # 截图服务
│   ├── single_website_service.py  # 单网站服务
│   ├── tts_server.py            # 文字转语音服务
│   ├── waresoft_launcher.py     # 软件启动器
│   └── windows_service.py       # Windows窗口管理服务
├── dpchatt/                    # 前端应用目录
│   ├── dist_electron/          # Electron打包配置
│   ├── public/                 # 公共资源
│   ├── src/                    # 源代码
│   │   ├── App.vue            # 主应用组件
│   │   ├── background.js      # Electron后台进程
│   │   ├── components/        # 组件目录
│   │   └── main.js            # 入口文件
│   ├── babel.config.js        # Babel配置
│   ├── jsconfig.json          # JS配置
│   ├── package.json           # 项目依赖和脚本
│   └── vue.config.js          # Vue CLI配置
└── start_all_services.py       # 一键启动所有后端服务的脚本
```

## 技术栈

### 前端
- **框架**：Vue 3
- **桌面应用**：Electron
- **构建工具**：Vue CLI
- **其他**：Babel, ESLint

### 后端
- **框架**：FastAPI
- **语音合成**：edge-tts
- **Windows API**：pywin32
- **其他**：pyautogui

## 系统要求

### 前端
- Node.js (推荐v14+)
- npm 或 yarn

### 后端
- Python 3.11
- Windows系统（部分功能依赖Windows API）

## 安装与配置

### 前端安装

1. 进入前端目录：
```bash
cd dpchatt
```

2. 安装依赖：
```bash
npm install
```

3. 运行开发服务器：
```bash
npm run electron:serve
```

4. 构建生产版本：
```bash
npm run electron:build
```

### 后端安装

1. 创建虚拟环境（推荐）：
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install fastapi uvicorn pywin32 pyautogui edge-tts
```

## 服务启动

### 方式一：使用启动脚本（推荐）

在项目根目录运行：
```bash
python start_all_services.py
```

这将自动启动所有后端服务。

### 方式二：手动启动单个服务

后端由多个独立服务组成，每个服务运行在不同的端口：

1. **动作收集器** (action_collector.py) - 端口 8005
```bash
python backend/action_collector.py
```

2. **动作执行器** (action_executor.py) - 端口 8008
```bash
python backend/action_executor.py
```

3. **日志监控服务** (log_monitor_service.py) - 端口 8010
```bash
python backend/log_monitor_service.py
```

4. **QQ聊天服务** (qqchat.py) - 端口 8002
```bash
python backend/qqchat.py
```

5. **截图服务** (screenshot_service.py) - 端口 8001
```bash
python backend/screenshot_service.py
```

6. **单网站服务** (single_website_service.py) - 端口 8004
```bash
python backend/single_website_service.py
```

7. **文字转语音服务** (tts_server.py) - 端口 8000
```bash
python backend/tts_server.py
```

8. **软件启动器** (waresoft_launcher.py) - 端口 8007
```bash
python backend/waresoft_launcher.py
```

9. **Windows窗口服务** (windows_service.py) - 端口 8009
```bash
python backend/windows_service.py
```

## 功能说明

### 智能对话系统

用户可以通过文本输入与AI进行对话，系统会保存对话历史，用户可以创建新对话、切换对话或删除历史对话。

### 语音交互

#### 文字转语音（TTS）
- 使用Edge TTS进行语音合成
- 支持多种语音和音调调整
- 实现音频缓存机制，提高响应速度
- 支持自动播放和手动播放两种模式

### 系统操作自动化

#### 自动发送QQ消息
- 通过Windows API操作QQ窗口
- 支持选择好友并发送消息
- 支持发送文件

#### 自动打开网站
- 从文本中提取URL
- 使用系统默认浏览器打开网站
- 支持批量打开多个网站

#### 自动打开软件
- 支持启动指定路径的软件
- 管理软件进程状态
- 防止重复启动

#### 执行系统命令
- 执行终端命令并捕获输出
- 支持命令执行结果返回

#### 窗口管理
- 置顶指定窗口
- 获取当前所有窗口列表
- 异步命令队列处理

#### 屏幕截图
- 使用pyautogui进行屏幕截图
- 将截图保存到指定目录
- 提供截图访问URL

### 日志监控

- 实时收集和显示系统日志
- 支持清除日志功能
- 检测特定触发器并执行相应操作

## API文档

### 动作收集器 (端口 8005)

#### POST /collect_actions
收集并决定指令执行顺序

**请求体**:
```json
{
  "message": "AI返回的消息内容"
}
```

**响应**:
```json
{
  "success": true,
  "actions": [...],
  "execution_order": [...]
}
```

### 动作执行器 (端口 8008)

#### POST /process_ai_message
处理AI消息，根据标记调用相应的服务

**请求体**:
```json
{
  "message": "AI的回答内容，可能包含[ACTION:OPENCMD]、[ACTION:RUN]或[ACTION:BG]标记"
}
```

**响应**:
```json
{
  "success": true,
  "message": "处理完成",
  "results": [
    {
      "action": "操作类型",
      "success": true,
      "message": "操作结果描述",
      "details": {...}
    }
  ]
}
```

**注意**：
- 支持的指令包括：[ACTION:OPENCMD]、[ACTION:RUN]、[ACTION:BG]
- [ACTION:OPENCMD]后跟要执行的命令
- [ACTION:RUN]后跟要执行的命令
- [ACTION:BG]后跟要后台执行的命令

### 日志监控服务 (端口 8010)

#### POST /add_log
添加日志到调试面板

**请求体**:
```json
{
  "timestamp": "2023-01-01 12:00:00",
  "type": "info",
  "message": "日志消息"
}
```

#### POST /get_debug_logs
获取调试面板的所有日志

**响应**:
```json
{
  "success": true,
  "logs": [...]
}
```

#### POST /clear_logs
清除所有日志

**响应**:
```json
{
  "success": true,
  "message": "日志已清除"
}
```

### QQ聊天服务 (端口 8002)

#### POST /send_qq_message
处理AI消息并发送QQ消息和文件

**请求体**:
```json
{
  "message": "包含[ACTION:SENDMESSAGE]和[ACTION:SELECTFRIEND]的消息"
}
```

**响应**:
```json
{
  "success": true,
  "message": "成功执行 1/1 个操作",
  "results": [
    {
      "action": "send_qq_message",
      "success": true,
      "message": "操作结果描述",
      "friend": "好友名称",
      "content": "消息内容"
    }
  ]
}
```

**注意**：
- 消息中必须包含[ACTION:SELECTFRIEND]和[ACTION:SENDMESSAGE]指令
- [ACTION:SELECTFRIEND]后跟好友名称
- [ACTION:SENDMESSAGE]后跟消息内容
- 也支持[ACTION:SENDFILE]指令发送文件

#### GET /health
健康检查接口

**响应**:
```json
{
  "status": "ok",
  "service": "QQ Message Service"
}
```

### 截图服务 (端口 8001)

#### POST /screenshot
执行截图

**请求体**:
```json
{
  "message": "AI的回答内容"
}
```

**响应**:
```json
{
  "success": true,
  "message": "截图成功",
  "screenshot_path": "截图文件路径",
  "screenshot_url": "http://localhost:8001/screenshots/1.png"
}
```

**注意**：截图URL中的端口为8001，与截图服务端口一致。

### 单网站服务 (端口 8004)

#### POST /open_website_from_message
从消息中提取并打开网址

**请求体**:
```json
{
  "message": "包含网址的消息内容"
}
```

**响应**:
```json
{
  "success": true,
  "message": "成功打开 1 个网址",
  "urls": ["http://example.com"],
  "count": 1
}
```

### 语音转文字服务 (端口 8006)

#### POST /transcribe
接收音频文件并进行语音识别

**请求**:
- Content-Type: multipart/form-data
- file: 音频文件

**响应**:
```json
{
  "success": true,
  "text": "识别出的文本",
  "duration": 5.23
}
```

### 文字转语音服务 (端口 8000)

#### POST /tts_dify
将文字转换为语音

**请求体**:
```json
{
  "text": "要转换的文字",
  "voice": "zh-CN-XiaoyiNeural",
  "pitch": "+10Hz",
  "rate": "-5%"
}
```

**响应**:
- Content-Type: audio/mpeg
- 音频数据

### 软件启动器 (端口 8007)

#### POST /api/qq/start
启动QQ

**响应**:
```json
{
  "status": "success",
  "message": "QQ started successfully",
  "pid": 12345
}
```

#### POST /api/qq/stop
停止QQ进程

**响应**:
```json
{
  "status": "success",
  "message": "QQ stopped successfully"
}
```

#### GET /api/qq/status
获取QQ运行状态

**响应**:
```json
{
  "status": "running",
  "pid": 12345
}
```

#### POST /api/qq/restart
重启QQ

**响应**:
```json
{
  "status": "success",
  "message": "QQ restarted successfully",
  "pid": 12345
}
```

#### POST /api/qq/check_and_start
检查AI回复并根据[ACTION:OPENSOFTWARE]后面的路径启动对应软件

**请求体**:
```json
{
  "message": "包含[ACTION:OPENSOFTWARE]的消息"
}
```

**响应**:
```json
{
  "status": "success",
  "message": "Successfully started 1 out of 1 software(s)",
  "results": [
    {
      "software_path": "软件路径",
      "status": "success",
      "message": "Software started successfully"
    }
  ]
}
```

#### GET /health
健康检查接口

**响应**:
```json
{
  "status": "healthy",
  "service": "qq_launcher"
}
```

#### GET /
根路径，显示服务信息

**响应**:
```json
{
  "service": "QQ Launcher",
  "version": "1.0.0"
}
```

### Windows窗口服务 (端口 8020)

#### POST /get_windows
获取所有可见窗口

**请求体**:
```json
{
  "message": "包含[ACTION:NOWWINDOWS]的消息"
}
```

**响应**:
```json
{
  "success": true,
  "message": "成功获取 10 个窗口",
  "windows": [
    {
      "handle": 窗口句柄,
      "title": "窗口标题",
      "class_name": "窗口类名"
    }
  ]
}
```

**注意**：消息中必须包含[ACTION:NOWWINDOWS]指令才会返回窗口列表。

#### POST /execute_actions
执行传入的指令列表

**请求体**:
```json
{
  "actions": [
    {
      "action_type": "TOPWINDOWS",
      "params": {
        "window_title": "窗口标题"
      }
    }
  ]
}
```

**响应**:
```json
{
  "success": true,
  "message": "处理完成",
  "results": [
    {
      "action": "set_window_topmost",
      "success": true,
      "message": "操作结果描述",
      "details": {
        "window": {
          "handle": 窗口句柄,
          "title": "窗口标题",
          "class_name": "窗口类名"
        }
      }
    }
  ]
}
```

**注意**：
- 支持的操作类型包括：TOPWINDOWS、SCREENSHOT、NOWWINDOWS
- 所有操作通过队列异步执行，按顺序处理
- 每个操作之间有1秒的间隔

## 使用说明

### 基本对话

1. 启动前端应用和所有后端服务
2. 在聊天界面输入文本消息
3. 点击发送按钮或按Enter键发送消息
4. 等待AI回复，回复会显示在聊天界面

### 语音交互

1. 点击麦克风图标开始录音
2. 说话结束后点击停止
3. 系统自动将语音转换为文字并发送给AI
4. AI回复后，如果启用了自动语音播放，系统会自动朗读回复

### 系统操作

AI可以通过特定指令执行系统操作，这些指令以`[ACTION:XXX]`的形式嵌入在AI回复中：

- `[ACTION:SCREENSHOT]` - 执行屏幕截图
- `[ACTION:SENDMESSAGE]好友名称消息内容` - 发送QQ消息
- `[ACTION:SELECTFRIEND]好友名称` - 选择QQ好友
- `[ACTION:OPENWEBSITE]http://example.com` - 打开网站
- `[ACTION:OPENSOFTWARE]软件路径` - 打开软件
- `[ACTION:OPENCMD]命令` - 执行命令
- `[ACTION:TOPWINDOWS]窗口标题` - 置顶窗口
- `[ACTION:NOWWINDOWS]` - 获取当前窗口列表
- `[ACTION:READLOG]消息内容` - 读取日志并发送消息

## 故障排除

### 前端问题

**问题：应用无法启动**
- 检查Node.js版本是否符合要求
- 删除node_modules文件夹并重新安装依赖
- 检查端口是否被占用

**问题：Electron打包失败**
- 确保electron-builder版本兼容
- 检查系统环境变量
- 查看错误日志获取详细信息

### 后端问题

**问题：Whisper模型加载失败**
- 检查NVIDIA驱动是否正确安装
- 确认CUDA和cuDNN版本兼容
- 检查模型文件是否完整下载

**问题：QQ自动化操作失败**
- 确保QQ客户端已正确安装
- 检查QQ窗口是否可被识别
- 以管理员权限运行服务

**问题：TTS服务无响应**
- 检查网络连接（Edge TTS需要网络）
- 清除音频缓存
- 检查文本内容是否包含特殊字符

## 开发指南

### 添加新的系统操作

1. 在action_collector.py中添加新的动作解析逻辑
2. 在相应的服务模块中实现API接口
3. 在action_executor.py中添加执行逻辑
4. 更新API文档

### 修改语音模型

1. 在stt_service.py中修改模型配置
2. 调整compute_type以适应不同GPU
3. 测试模型性能和准确率

### 自定义TTS语音

1. 在tts_server.py中修改默认语音参数
2. 调整pitch和rate参数以获得理想效果
3. 测试不同语音选项

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交问题报告和改进建议。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件至项目维护者
