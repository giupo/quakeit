var getConfig = require('hjs-webpack');

module.exports = getConfig({
  in: "src/app.js",
  out: "public",
  clearBeforeBuild: true,
  isDev: process.env.NODE_ENV !== 'production',
 
  devServer: {
    inline: true,
    hot: true,
    devtool: true,
    proxy: {
      '/data/*': 'http://localhost:8080/'
    }
  }
});
