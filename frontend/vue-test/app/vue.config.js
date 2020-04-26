module.exports = {
  pluginOptions: {
    quasar: {
      treeShake: true
    }
  },
  transpileDependencies: [
    /[\\\/]node_modules[\\\/]quasar[\\\/]/
  ],
  devServer: {
    host: '0.0.0.0',
    port: 80
    // proxy: 'http://localhost:8000/',
  }

}
