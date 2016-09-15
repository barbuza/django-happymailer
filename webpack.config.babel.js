import { resolve } from 'path';
import autoprefixer from 'autoprefixer';
import { EnvironmentPlugin, NoErrorsPlugin } from 'webpack';
import UglifyJsPlugin from 'webpack/lib/optimize/UglifyJsPlugin';

const config = {
  context: resolve('.'),
  entry: {
    client: './happymailer/src/index'
  },
  output: {
    path: resolve('happymailer/static/happymailer'),
    filename: '[name].js',
    publicPath: ''
  },
  module: {
    loaders: [
      {
        test: /\/[A-Z][^\/]*\.js$/,
        exclude: /node_modules/,
        loaders: ['baggage?[file].scss=styles', 'babel']
      },
      {
        test: /\.jsx$/,
        loaders: ['babel']
      },
      {
        test: /\/[a-z][^\/]*\.js$/,
        exclude: /node_modules/,
        loaders: ['babel']
      },
      {
        test: /\.css$/,
        loaders: ['style', 'css']
      },
      {
        test: /\/[A-Z][^\/]*\.scss$/,
        loaders: [
          'style',
          'css?module&importLoader=1&localIdentName=[name]_[local]_[hash:hex:5]',
          'postcss?pack=general',
          'sass'
        ]
      },
      {
        test: /\.svg$/,
        loaders: ['file']
      }
    ]
  },
  postcss: {
    general: [
      autoprefixer({
        browsers: ['last 3 versions']
      })
    ]
  },
  plugins: [
    new EnvironmentPlugin([
      'NODE_ENV'
    ]),
    new NoErrorsPlugin()
  ]
};

if (process.env.NODE_ENV === 'production') {
  config.plugins.push(new UglifyJsPlugin({ comments: /a^/, compress: { warnings: false } }));
}

export default config;
