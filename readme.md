# DPChat - 智能对话助手

一个基于Vue.js和FastAPI的智能对话助手，支持通过自然语言执行系统命令、管理窗口、发送QQ消息等多种操作。

## 功能特性

- 🤖 **智能对话**：与Dify AI进行自然语言对话
- 💻 **CMD命令执行**：通过自然语言执行系统命令
- 🪟 **窗口管理**：查看、置顶当前打开的窗口
- 🖱️ **自动化操作**：图像识别自动点击按钮
- 💬 自动**发送消息**：自动发送QQ/微信消息和文件
- 📊 **调试面板**：实时查看操作日志
- 🌙 **深色模式**：支持深色/浅色主题切换

## 系统要求

- Node.js 16.x 或更高版本
- Python 3.8 或更高版本
- Windows 操作系统

## 项目结构

```
dpchatt/
├── backend/              # 后端服务
│   ├── CMD_EXECUTOR.py           # CMD命令执行服务 (端口: 8008)
│   ├── WINDOWS_MANAGER.py        # 窗口管理服务 (端口: 8020)
│   ├── OPENCV_CHECK.py           # 图像识别按钮点击服务 (端口: 8023)
│   ├── QQ_SELECTFREND_SENDMESSAGE.py  # QQ/微信 消息发送服务 (端口: 8021)
│   ├── QQ_SELECTFREND_SENDFILE.py     # QQ/微信 文件发送服务 (端口: 8025)
│   └── dify_proxy.py             # Dify API代理服务 (端口: 8009)
└── dpchatt/              # 前端应用
    ├── src/
    │   ├── App.vue               # 主应用组件
    │   └── components/
    │       └── debugpanel.vue    # 调试面板组件
    └── package.json
```

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd AIchatbot
```

2. 安装前端依赖（npm install若出现网络问题请先在cmd中使用set ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/尝试设置镜像）

```bash
cd dpchatt
npm install
```

### 3. 安装后端依赖

```bash
cd ../backend
pip install -r requirements.txt
```

如果没有requirements.txt，请手动安装以下依赖：

```bash
pip install fastapi uvicorn python-multipart opencv-python pyautogui pywinauto
```

## 配置说明

### 后端服务配置

各后端服务默认运行在以下端口：

- CMD执行服务：8008
- Dify代理服务：8009
- 窗口管理服务：8020
- QQ消息服务：8021
- 按钮点击服务：8023
- QQ文件服务：8025

### 前端配置

在dify_proxy.py第26行中配置Dify API地址：

```javascript
DIFY_API_KEY = "请输入你的dify agent api"
```

## 启动指南

1. 启动后端服务（如果需要，您完全可以自己动手试着写一个启动所有服务的后端脚本在backend文件夹，并以此来建立对此项目后端功能的理解）

打开多个终端窗口，分别启动各个服务：

```bash
（# 终端1 - CMD执行服务
cd backend
python CMD_EXECUTOR.py

# 终端2 - 窗口管理服务
python WINDOWS_MANAGER.py

# 终端3 - 按钮点击服务
python OPENCV_CHECK.py

# 终端4 - QQ消息服务
python QQ_SELECTFREND_SENDMESSAGE.py

# 终端5 - QQ文件服务
python QQ_SELECTFREND_SENDFILE.py

# 终端6 - Dify代理服务
python dify_proxy.py
```

### 2. 构建前端应用

```bash
cd dpchatt
npm run electron:build

```

或使用开发模式进行调试：

npm run electron:serve

### 3. 访问应用

打开浏览器访问：`http://localhost:8080`

## 使用说明

### 基本对话

直接在输入框中输入消息，按Enter键或点击"发送"按钮即可与AI对话。

### 执行CMD命令

AI会自动识别需要执行的命令，例如：

```
用户：帮我打开Dify网站
AI回复：好的，我来帮你打开Dify网站。
[ACTION:OPENCMD]start https://cloud.dify.ai
```

系统会自动执行 `start https://cloud.dify.ai`命令。

### 窗口管理

- 查看当前窗口：询问"当前打开了哪些窗口"
- 置顶窗口：指定窗口名称进行置顶

### 发送消息

（微信和QQ都可使用，但是界面需要设置为单独面板让其不自动隐藏，而是作为一个窗口，目前为test版本）

```
用户：给张三发送消息"你好"
AI回复：好的，正在给张三发送消息...
[ACTION:SELECTFRIEND_SENDMESSAGE]张三|你好
```

### 图像识别按钮点击

依赖backend中已保存的图片名称自动在桌面上识别图片，如果您有新的需求，在backend文件夹下设置一个新的文件夹并将需要点击的图片设置好名称放入其中，就可支持此功能。

### 调试面板

点击工具栏上的"调试面板"按钮可以查看详细的操作日志，包括：

- 命令执行时间
- 命令执行结果
- 错误信息

支持的指令格式

系统支持以下ACTION指令：

- `[ACTION:OPENCMD]` - 执行CMD命令
- `[ACTION:NOWWINDOWS]` - 获取当前窗口列表
- `[ACTION:TOPWINDOWS]` - 置顶指定窗口
- `[ACTION:CLICKBUTTON]` - 点击指定按钮
- `[ACTION:SELECTFRIEND_SENDMESSAGE]` - 发送QQ消息
- `[ACTION:SELECTFRIEND_SENDFILE]` - 发送QQ文件
- `[ACTION:READLOG]` - 让ai查看日志

## 常见问题

### Q: CMD命令没有执行？

A: 请检查：

1. CMD执行服务（端口8008）是否正常运行
2. 浏览器控制台是否有错误信息
3. 调试面板中是否显示命令执行日志

### Q: 窗口管理功能不工作？

A: 请确保：

1. 窗口管理服务（端口8020）正在运行
2. 窗口名称与实际窗口标题完全匹配

### Q: QQ消息发送失败？

A: 请检查：

1. QQ消息服务（端口8021）正在运行
2. 好友名称准确无误
3. QQ客户端已登录

## 开发说明

### 添加新的ACTION指令

1. 在前端 `App.vue`的 `actionRegex`中添加新的指令类型
2. 在 `switch`语句中添加处理逻辑
3. 创建对应的后端服务
4. 在后端服务中实现指令解析和执行逻辑

### 调试技巧

1. 打开浏览器开发者工具（F12）查看控制台日志
2. 使用调试面板查看详细的操作日志
3. 检查各后端服务的运行日志

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请提交Issue或联系项目维护者。

    QQ:2195786717@qq.com
