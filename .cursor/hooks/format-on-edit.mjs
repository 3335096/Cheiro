// Formats files right after an agent edits them, using the project's own tools.
// Silent and fail-open: if tooling is not installed yet, the hook does nothing.
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
const isWindows = process.platform === "win32";

function readInput() {
  try {
    return JSON.parse(readFileSync(0, "utf8"));
  } catch {
    return {};
  }
}

const filePath = readInput().file_path;
if (!filePath || !existsSync(filePath)) process.exit(0);

const rel = relative(root, filePath);
if (rel.startsWith("..")) process.exit(0);
const top = rel.split(sep)[0];

function exec(command, args, cwd) {
  spawnSync(command, args, { cwd, stdio: "ignore", shell: isWindows && command.endsWith(".cmd") });
}

if (top === "backend" && filePath.endsWith(".py")) {
  const python = isWindows
    ? join(root, "backend", ".venv", "Scripts", "python.exe")
    : join(root, "backend", ".venv", "bin", "python");
  if (existsSync(python)) {
    exec(python, ["-m", "ruff", "check", "--fix", "--quiet", filePath], join(root, "backend"));
    exec(python, ["-m", "ruff", "format", "--quiet", filePath], join(root, "backend"));
  }
} else if ((top === "frontend" || top === "admin") && /\.(tsx?|css|json)$/.test(filePath)) {
  const bin = join(root, top, "node_modules", ".bin", isWindows ? "prettier.cmd" : "prettier");
  if (existsSync(bin)) exec(bin, ["--write", filePath], join(root, top));
}

process.exit(0);
