/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 0);
/******/ })
/************************************************************************/
/******/ ({

/***/ "./src/background.js":
/*!***************************!*\
  !*** ./src/background.js ***!
  \***************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("const { app, BrowserWindow, Menu, ipcMain } = __webpack_require__(/*! electron */ \"electron\")\r\n\r\nlet mainWindow\r\n\r\nfunction createWindow() {\r\n  mainWindow = new BrowserWindow({\r\n    width: 600,\r\n    height: 800,\r\n    backgroundColor: '#1e1e1e',\r\n    webPreferences: {\r\n      nodeIntegration: true,\r\n      contextIsolation: false\r\n    }\r\n  })\r\n\r\n  // 移除菜单栏\r\n  Menu.setApplicationMenu(null)\r\n\r\n  // 开发环境下加载开发服务器的URL\r\n  if (true) {\r\n    mainWindow.loadURL(\"http://localhost:8080/\")\r\n    // 打开开发者工具\r\n    if (!process.env.IS_TEST) {\r\n      mainWindow.webContents.openDevTools()\r\n    }\r\n  } else {}\r\n\r\n  mainWindow.on('closed', () => {\r\n    mainWindow = null\r\n  })\r\n\r\n  // 处理置顶窗口的IPC通信\r\n  ipcMain.on('toggle-always-on-top', (event, isAlwaysOnTop) => {\r\n    if (mainWindow) {\r\n      mainWindow.setAlwaysOnTop(isAlwaysOnTop)\r\n    }\r\n  })\r\n}\r\n\r\napp.on('ready', createWindow)\r\n\r\napp.on('window-all-closed', () => {\r\n  if (process.platform !== 'darwin') {\r\n    app.quit()\r\n  }\r\n})\r\n\r\napp.on('activate', () => {\r\n  if (mainWindow === null) {\r\n    createWindow()\r\n  }\r\n})\r\n\n\n//# sourceURL=webpack:///./src/background.js?");

/***/ }),

/***/ 0:
/*!*********************************!*\
  !*** multi ./src/background.js ***!
  \*********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("module.exports = __webpack_require__(/*! C:\\Users\\21957\\Desktop\\dpchattttt\\dpchatt\\src\\background.js */\"./src/background.js\");\n\n\n//# sourceURL=webpack:///multi_./src/background.js?");

/***/ }),

/***/ "electron":
/*!***************************!*\
  !*** external "electron" ***!
  \***************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("module.exports = require(\"electron\");\n\n//# sourceURL=webpack:///external_%22electron%22?");

/***/ })

/******/ });