const path = require("path");
const webpack = require("webpack");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const AssetsPlugin = require("assets-webpack-plugin");

module.exports = {
  entry: {
    main: path.join(__dirname, "src", "index.js")
  },

  output: {
    path: path.join(__dirname, "public")
  },

  module: {
    rules: [
      {
        loader: "babel-loader",
        test: /\.js$/,
        exclude: /node_modules/,
        query: {
          cacheDirectory: true
        }
      }
    ]
  },

  plugins: [
    new AssetsPlugin({
      filename: "webpack.json",
      path: path.join(process.cwd(), "data"),
      prettyPrint: true
    })
  ]
};
