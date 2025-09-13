const express = require("express");
const path = require("path");
const fs = require("fs");
const readline = require("readline");

const app = express();

// Base folder = "first lang"
const baseFolder = path.join(__dirname, "first lang");
app.use(express.static(baseFolder));

let previewPath = process.argv[2] ? path.resolve(process.argv[2]) : null;

// Helper: latest compiled file
function getLatestCompiled(folder) {
  if (!fs.existsSync(folder)) return null;
  const files = fs.readdirSync(folder)
    .filter(f => f.endsWith("_compiled.html"))
    .map(f => ({
      f,
      mtime: fs.statSync(path.join(folder, f)).mtime.getTime()
    }))
    .sort((a, b) => b.mtime - a.mtime);
  return files.length > 0 ? path.join(folder, files[0].f) : null;
}

// Normalize preview path
if (previewPath && fs.existsSync(previewPath)) {
  const stats = fs.statSync(previewPath);
  if (stats.isDirectory()) {
    previewPath = getLatestCompiled(previewPath);
  }
} else {
  previewPath = null;
}

// Serve index
app.get("/", (req, res) => {
  if (previewPath && fs.existsSync(previewPath)) {
    return res.sendFile(path.basename(previewPath), { root: path.dirname(previewPath) });
  }

  const compiledFolder = path.join(baseFolder, "N# projects", "compiled");
  const latestFile = getLatestCompiled(compiledFolder);

  if (latestFile) {
    return res.sendFile(path.basename(latestFile), { root: path.dirname(latestFile) });
  } else {
    return res.send("⚠️ No compiled N# file found!");
  }
});

const PORT = 80;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Serving first lang at http://localhost:${PORT}/`);
  if (previewPath) {
    console.log(`Previewing file: ${previewPath}`);
  }
  console.log("Press ENTER to stop the server...");
});

// Pause like batch "pause"
readline.createInterface({
  input: process.stdin,
  output: process.stdout
}).question("", () => {
  process.exit(0);
});
