import { copyFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { BACKEND, FRONTEND, IS_WINDOWS, ROOT, VENV_PYTHON, npm, run } from "./lib.mjs";

// First-time setup, safe to re-run.
const systemPython = IS_WINDOWS ? "py" : "python3";
const pythonArgs = IS_WINDOWS ? ["-3.12"] : [];

if (!existsSync(VENV_PYTHON)) {
  run(systemPython, [...pythonArgs, "-m", "venv", ".venv"], { cwd: BACKEND });
}
run(VENV_PYTHON, ["-m", "pip", "install", "--quiet", "--upgrade", "pip"], { cwd: BACKEND });
run(VENV_PYTHON, ["-m", "pip", "install", "--quiet", "-r", "requirements-dev.txt"], { cwd: BACKEND });
npm(["ci"], { cwd: FRONTEND });

const envFile = join(ROOT, ".env");
if (!existsSync(envFile)) {
  copyFileSync(join(ROOT, ".env.example"), envFile);
  console.log("\nCreated .env from .env.example. Add OPENROUTER_API_KEY before running the RAG pipeline.");
}

console.log("\nSetup complete. Next: npm run check, then npm run dev");
