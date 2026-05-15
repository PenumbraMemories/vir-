const { defineConfig } = require('@vue/cli-service')
const path = require('path')

module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: './',
  pluginOptions: {
    electronBuilder: {
      mainProcessFile: 'src/background.js',
      mainProcessWatch: ['src/background.js'],
      mainProcessEntryPoint: 'src/background.js',
      nodeIntegration: true,
      contextIsolation: false,
      outputDir: 'dist_electron/bundled',
      builderOptions: {
        asar: false
      },
      customFileProtocol: './',
      // 确保 package.json 中包含 main 字段
      extendPackage: {
        main: 'background.js',
        description: 'DPChatt Application',
        author: 'DPChatt Team'
      },
      builder: {
        appId: 'com.dpchatt.app',
        productName: 'DPChatt',
        directories: {
          output: 'dist_electron'
        },
        win: {
          target: [
            {
              target: 'nsis',
              arch: [
                'x64'
              ]
            }
          ],
          icon: 'public/icon.ico',
          artifactName: '${productName}-${version}-${arch}.${ext}'
        },
        nsis: {
          oneClick: false,
          allowElevation: true,
          allowToChangeInstallationDirectory: true,
          installerIcon: 'public/icon.ico',
          uninstallerIcon: 'public/icon.ico',
          installerHeaderIcon: 'public/icon.ico',
          createDesktopShortcut: true,
          createStartMenuShortcut: true,
          shortcutName: 'DPChatt'
        }
      }
    }
  },
  configureWebpack: {
    output: {
      filename: 'js/[name].[contenthash:8].js',
      chunkFilename: 'js/[name].[contenthash:8].js'
    },
    optimization: {
      splitChunks: {
        chunks: 'all'
      }
    }
  },
  chainWebpack: config => {
    config.plugin('html').tap(args => {
      args[0].filename = 'index.html'
      return args
    })
  }
})
