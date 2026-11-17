import { git } from "./lib.mjs";

// Brings this machine in line with GitHub without ever overwriting work:
//   - fetches everything (including branches cloud agents pushed from your phone)
//   - fast-forwards/rebases the current branch only when the tree is clean
//   - shows which agent branches are new and which of your branches need a push
// It never force-pushes, resets, or deletes anything.
const out = (args) => (git(args).stdout ?? "").trim();
const lines = (text) => text.split("\n").filter(Boolean);

const fetched = git(["fetch", "--all", "--prune"]);
if (fetched.status !== 0) {
  console.error("git fetch failed. Check your network and GitHub credentials.\n" + (fetched.stderr ?? ""));
  process.exit(1);
}

const branch = out(["rev-parse", "--abbrev-ref", "HEAD"]);
const dirty = lines(out(["status", "--porcelain"])).length > 0;
const upstream = out(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]);

console.log(`Branch: ${branch}${dirty ? "  (uncommitted changes)" : ""}`);

if (!upstream || upstream.startsWith("fatal")) {
  console.log(`No upstream for ${branch}. Publish it with: git push -u origin ${branch}`);
} else {
  const [ahead, behind] = out(["rev-list", "--left-right", "--count", `HEAD...${upstream}`])
    .split(/\s+/)
    .map(Number);
  console.log(`Upstream ${upstream}: ${ahead} ahead, ${behind} behind`);
  if (behind > 0 && dirty) {
    console.log("Behind GitHub but you have uncommitted changes: commit or stash, then run sync again.");
  } else if (behind > 0) {
    const pulled = git(["pull", "--rebase", "--autostash"]);
    if (pulled.status === 0) {
      console.log(`Updated ${branch} from GitHub (rebased).`);
    } else {
      console.log("Rebase hit conflicts. Resolve them, then: git rebase --continue (or git rebase --abort).");
      console.log(pulled.stderr ?? "");
      process.exit(1);
    }
  } else if (ahead > 0) {
    console.log(`You have ${ahead} commit(s) not on GitHub. Push with: git push`);
  } else {
    console.log("Up to date.");
  }
}

const mainRef = out(["rev-parse", "--verify", "--quiet", "origin/main"]) ? "origin/main" : "origin/master";

const agentBranches = lines(
  out([
    "for-each-ref",
    "--sort=-committerdate",
    "--format=%(refname:short)|%(committerdate:relative)|%(authorname)|%(subject)",
    "refs/remotes/origin/cursor/",
  ]),
).filter((row) => {
  const ref = row.split("|")[0];
  return out(["rev-list", "--count", `${mainRef}..${ref}`]) !== "0";
});

console.log("\nCloud-agent branches with work not yet merged into main:");
if (agentBranches.length === 0) {
  console.log("  none");
} else {
  for (const row of agentBranches) {
    const [ref, when, , subject] = row.split("|");
    console.log(`  ${ref}  (${when})  ${subject}`);
  }
  console.log("  Review the PR on GitHub, or check one out: git checkout <name without origin/>");
}

const localOnly = lines(
  out(["for-each-ref", "--format=%(refname:short)|%(upstream)|%(upstream:track)", "refs/heads/"]),
)
  .map((row) => row.split("|"))
  .filter(([, remote, track]) => remote === "" || track === "[gone]")
  .map(([name]) => name)
  .filter((name) => name !== "main" && name !== "master");

if (localOnly.length > 0) {
  console.log("\nLocal branches not on GitHub (unpublished, or merged and deleted remotely):");
  for (const name of localOnly) console.log(`  ${name}`);
}
