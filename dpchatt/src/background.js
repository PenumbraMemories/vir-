const { app, BrowserWindow, Menu, ipcMain } = require('electron')

let mainWindow

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 600,
    height: 800,
    backgroundColor: '#1e1e1e',
    alwaysOnTop: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  })

  // 将Electron的IPC通信暴露给渲染进程
  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.webContents.executeJavaScript(`
      window.electron = {
        send: (channel, data) => {
          require('electron').ipcRenderer.send(channel, data);
        }
      };
    `);
  });

  // 移除菜单栏
  Menu.setApplicationMenu(null)

  // 开发环境下加载开发服务器的URL
  if (process.env.WEBPACK_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.WEBPACK_DEV_SERVER_URL)
    // 打开开发者工具
    if (!process.env.IS_TEST) {
      mainWindow.webContents.openDevTools()
    }
  } else {
    // 生产环境下加载打包后的index.html
    const path = require('path')
    mainWindow.loadFile(path.join(__dirname, 'index.html'))
    // 确保资源路径正确
    mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
      console.error('Failed to load:', errorCode, errorDescription)
    })
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  // 处理置顶窗口的IPC通信
  ipcMain.on('toggle-always-on-top', (event, isAlwaysOnTop) => {
    if (mainWindow) {
      mainWindow.setAlwaysOnTop(isAlwaysOnTop)
    }
  })
}

app.on('ready', createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})
