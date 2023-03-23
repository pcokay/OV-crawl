const { spawn } = require("child_process");

exports.handler = async (event, context) => {
  const python = spawn("python", ["app.py"]);

  return new Promise((resolve, reject) => {
    python.stdout.on("data", (data) => {
      resolve({ statusCode: 200, body: data.toString() });
    });

    python.stderr.on("data", (data) => {
      console.error(`stderr: ${data}`);
    });

    python.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}`));
      }
    });
  });
};
