import { resolve } from "path";
import webpack from "webpack";

/**
 * @type {webpack.Configuration}
 */
const config = {
  context: resolve("."),
  entry: {
    client: "./happymailer/src/index",
  },
  output: {
    path: resolve("happymailer/static/happymailer"),
    filename: "[name].js",
    publicPath: "",
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "swc-loader",
          options: {
            jsc: {
              parser: {
                syntax: "ecmascript",
                jsx: true,
              },
            },
          },
        },
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\/[A-Z][^\/]*\.scss$/,
        use: [
          "style-loader",
          "css-loader?modules=local&importLoaders=1",
          "sass-loader",
        ],
      },
    ],
  },
};

export default config;
