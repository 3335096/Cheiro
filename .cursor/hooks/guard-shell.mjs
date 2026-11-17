// Blocks the two git mistakes that are expensive in this project:
//   1. force-pushing or pushing straight to main
//   2. committing secrets (.env files, API keys, Telegram bot tokens, private keys)
// Always prints a valid JSON decision (invalid output would block the command).
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";

function readInput() {
  try {
    return JSON.parse(readFileSync(0, "utf8"));
  } catch {
    return {};
  }
}

function decide(permission, message) {
  const payload = { permission };
  if (message) {
    payload.user_message = message;
    payload.agent_message = message;
  }
  process.stdout.write(JSON.stringify(payload));
  process.exit(0);
}

const { command = "", cwd } = readInput();

if (/\bgit\s+push\b/.test(command)) {
  const forced = /\s(--force(?!-with-lease)|-f)(\s|$)/.test(command) || /\s\+\S+/.test(command.split("push")[1] ?? "");
  const toMain = /(^|\s|:)(refs\/heads\/)?(main|master)(\s|$)/.test(command.split("push")[1] ?? "");
  if (forced) {
    decide("deny", "Force-push is blocked. Use --force-with-lease on your own branch only if you must.");
  }
  if (toMain) {
    decide("deny", "Direct pushes to main are blocked. Push a feature branch and open a pull request.");
  }
}

if (/\bgit\s+commit\b/.test(command)) {
  const git = (args) => spawnSync("git", args, { cwd, encoding: "utf8" }).stdout ?? "";

  const staged = git(["diff", "--cached", "--name-only"]).split("\n").filter(Boolean);
  const envFiles = staged.filter((f) => /(^|\/)\.env(\.[^/]+)?$/.test(f) && !f.endsWith(".env.example"));
  if (envFiles.length > 0) {
    decide("deny", `Refusing to commit environment files: ${envFiles.join(", ")}. Unstage them (git restore --staged).`);
  }

  const added = git(["diff", "--cached", "-U0"])
    .split("\n")
    .filter((line) => line.startsWith("+") && !line.startsWith("+++"))
    .join("\n");
  const patterns = [
    [/sk-or-v1-[A-Za-z0-9]{20,}/, "OpenRouter API key"],
    [/sk-[A-Za-z0-9]{32,}/, "API key"],
    [/\b\d{8,10}:[A-Za-z0-9_-]{35}\b/, "Telegram bot token"],
    [/-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----/, "private key"],
    [/gh[pousr]_[A-Za-z0-9]{36,}/, "GitHub token"],
    [/AKIA[0-9A-Z]{16}/, "AWS access key"],
  ];
  for (const [pattern, label] of patterns) {
    if (pattern.test(added)) {
      decide("deny", `Staged changes appear to contain a ${label}. Remove it and use an environment variable instead.`);
    }
  }
}

decide("allow");
