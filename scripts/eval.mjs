import { python } from "./lib.mjs";

// Runs the RAG golden set against the live index and writes docs/eval/<timestamp>.md
// Needs the database up with indexed books and OPENROUTER_API_KEY in the environment.
python(["-m", "evals.run_eval", ...process.argv.slice(2)]);
