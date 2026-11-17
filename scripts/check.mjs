import { FRONTEND, npm, python } from "./lib.mjs";

// One command for the same checks that CI runs.
//   npm run check               backend + frontend (no database needed)
//   npm run check:integration   adds pgvector tests (needs: docker compose up -d postgres)
//   npm run fix                 auto-fix and format
const flags = new Set(process.argv.slice(2));
const only = flags.has("--backend") ? "backend" : flags.has("--frontend") ? "frontend" : null;
const backend = only !== "frontend";
const frontend = only !== "backend";

if (flags.has("--fix")) {
  python(["-m", "ruff", "check", ".", "--fix"], { allowFail: true });
  python(["-m", "ruff", "format", "."]);
  npm(["run", "format"], { cwd: FRONTEND });
  process.exit(0);
}

if (backend) {
  python(["-m", "ruff", "check", "."]);
  python(["-m", "ruff", "format", "--check", "."]);
  python(["-m", "mypy", "app", "tests", "evals"]);
  if (flags.has("--integration")) {
    python(["-m", "pytest", "-o", "addopts=", "-q"]);
  } else {
    python(["-m", "pytest", "-q"]);
  }
}

if (frontend) {
  npm(["run", "lint"], { cwd: FRONTEND });
  npm(["run", "format:check"], { cwd: FRONTEND });
  npm(["run", "typecheck"], { cwd: FRONTEND });
  npm(["test"], { cwd: FRONTEND });
  npm(["run", "build"], { cwd: FRONTEND });
}

console.log("\nAll checks passed.");
