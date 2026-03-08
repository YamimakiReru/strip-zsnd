import archiver from "archiver";
import { createRequire } from "module";
import { spawnSync } from "node:child_process";
import process from "node:process";
import fs from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import os from "node:os";

const require = createRequire(import.meta.url);
const pkg = require("./package.json");

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
process.chdir(__dirname);

npx("rspack", "build");
npx(
  "tailwindcss",
  "-i",
  path.resolve(__dirname, "src/style.css"),
  "-o",
  path.resolve(__dirname, "dist/style.css"),
);
fs.copyFileSync(
  path.resolve(__dirname, "public/messages.js"),
  path.resolve(__dirname, "dist/messages.js"),
);

npx("opener", path.resolve(__dirname, "dist/index.html"));

const zipfs = fs.createWriteStream(
  `${__dirname}/dist/${pkg.name}-${pkg.version}-browser.zip`,
);
const zipper = archiver("zip", { zlib: { level: 9 } });
zipfs.on("close", () =>
  console.info(`Compression complete: ${zipper.pointer()} bytes`),
);
zipper.pipe(zipfs);
zipper.glob("*.html", { cwd: `${__dirname}/dist` });
zipper.glob("*.js", { cwd: `${__dirname}/dist` });
zipper.glob("*.css", { cwd: `${__dirname}/dist` });
zipper.glob("*.map", { cwd: `${__dirname}/dist` });
zipper.file(path.resolve(__dirname, "../README.md"), { name: "README.md" });
zipper.file(path.resolve(__dirname, "../LICENSE"), { name: "LICENSE" });
await zipper.finalize();

function npx(command, ...args) {
  const isWin = os.platform() === "win32";
  const commandPath = path.resolve(
    __dirname,
    `node_modules/.bin/${command}${isWin ? ".cmd" : ""}`,
  );
  spawnSync(commandPath, args, { stdio: "inherit", shell: true });
}
