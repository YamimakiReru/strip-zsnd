import { spawnSync } from "node:child_process";
import process from "node:process"
import fs from "node:fs"
import { fileURLToPath } from "node:url"
import path from "node:path"
import os from "node:os"

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
process.chdir(__dirname)

npx("rspack", "build")
npx("tailwindcss",
  "-i", path.resolve(__dirname, "src/style.css"),
  "-o", path.resolve(__dirname, "dist/style.css"))
fs.copyFileSync(
  path.resolve(__dirname, "public/index.html"),
  path.resolve(__dirname, "dist/index.html"))

function npx(command, ...args) {
  const isWin = os.platform() === "win32"
  const commandPath = path.resolve(__dirname,
    `node_modules/.bin/${command}${isWin ? ".cmd" : ""}`)
  spawnSync(commandPath, args, { stdio: "inherit", shell: true })
}
