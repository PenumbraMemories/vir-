const { defineConfig } = require('@vue/cli-service')
const path = require('path')

module.exports = defineConfig({
  transpileDependencies: true,
  pluginOptions: {
    electronBuilder: {
      mainProcessFile: 'src/background.js',
      mainProcessWatch: ['src/background.js'],
      nodeIntegration: true,
      contextIsolation: false,
      builder: {
        appId: 'com.dpchatt.app',
        productName: 'DPChatt',
        win: {
          target: 'nsis',
          icon: 'public/icon.ico'
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
