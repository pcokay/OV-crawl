const path = require('path');

module.exports = {
  entry: './src_functions/app.py',
  output: {
    path: path.join(__dirname, 'functions_build'),
    filename: 'app.js',
  },
};