import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
export const BACKEND = join(ROOT, "backend");
export const FRONTEND = join(ROOT, "frontend");
export const IS_WINDOWS = process.platform === "win32";

export const VENV_PYTHON = IS_WINDOWS
  ? join(BACKEND, ".venv", "Scripts", "python.exe")
  : join(BACKEND, ".venv", "bin", "python");

const NPM = IS_WINDOWS ? "npm.cmd" : "npm";

export function run(command, args, { cwd = ROOT, quiet = false, allowFail = false } = {}) {
  if (!quiet) console.log(`\n> ${[command, ...args].join(" ")}  (${cwd.replace(ROOT, ".") || "."})`);
  const result = spawnSync(command, args, {
    cwd,
    stdio: quiet ? ["ignore", "pipe", "pipe"] : "inherit",
    encoding: "utf8",
    shell: IS_WINDOWS && command.endsWith(".cmd"),
  });
  if (result.error) {
    console.error(`Cannot run "${command}": ${result.error.message}`);
    if (!allowFail) process.exit(1);
  }
  if (result.status !== 0 && !allowFail) process.exit(result.status ?? 1);
  return result;
}

export function npm(args, opts) {
  return run(NPM, args, opts);
}

export function python(args, opts) {
  if (!existsSync(VENV_PYTHON)) {
    console.error("Backend virtualenv not found. Run: npm run setup");
    process.exit(1);
  }
  return run(VENV_PYTHON, args, { cwd: BACKEND, ...opts });
}

export function git(args, opts = {}) {
  return run("git", args, { quiet: true, allowFail: true, ...opts });
}
