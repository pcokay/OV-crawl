const path = require('path');

module.exports = {
  entry: './src_functions/handler.js', // Make sure this is the correct path to your handler.js file
  output: {
    filename: 'handler.js',
    path: path.resolve(__dirname, 'functions_build'),
    libraryTarget: 'commonjs',
  },
  target: 'node',
  mode: 'production',
  externals: {
    'aws-sdk': 'aws-sdk',
  },
};
