"""Run the RAG golden set against the live index and write a Markdown report.

Usage (from backend/, with the database and OPENROUTER_API_KEY configured):
    python -m evals.run_eval
    python -m evals.run_eval --only life_line_basics

Checks per question:
  retrieval  - every title in `expected_source_titles` appears among retrieved sources
  include    - every phrase in `must_include` appears in the answer (case-insensitive)
  exclude    - no phrase in `must_not_include` appears in the answer
  cited      - at least one source was retrieved
A question with empty expectations only has the `cited` and `exclude` checks, so fill them in
as soon as the corpus is loaded.
"""

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.rag.pipeline import rag_answer

GOLDEN_PATH = Path(__file__).parent / "rag_golden.json"
REPORT_DIR = Path(__file__).resolve().parents[2] / "docs" / "eval"


@dataclass
class CaseResult:
    case_id: str
    query: str
    answer: str
    sources: list[dict]
    checks: dict[str, bool] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return all(self.checks.values())


def evaluate(case: dict, answer: str, sources: list[dict]) -> dict[str, bool]:
    titles = {s.get("title") for s in sources}
    lowered = answer.lower()
    return {
        "cited": bool(sources),
        "retrieval": all(t in titles for t in case.get("expected_source_titles", [])),
        "include": all(p.lower() in lowered for p in case.get("must_include", [])),
        "exclude": not any(p.lower() in lowered for p in case.get("must_not_include", [])),
    }


def render_report(results: list[CaseResult]) -> str:
    settings = get_settings()
    passed = sum(r.passed for r in results)
    lines = [
        f"# RAG eval {datetime.now(UTC):%Y-%m-%d %H:%M} UTC",
        "",
        f"- LLM: `{settings.llm_model}`",
        f"- Embeddings: `{settings.embedding_model}`",
        f"- Chunks: size {settings.rag_chunk_size}, overlap {settings.rag_chunk_overlap}, "
        f"top_k {settings.rag_top_k}",
        f"- Result: **{passed}/{len(results)} passed**",
        "",
    ]
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        failed = [name for name, ok in r.checks.items() if not ok]
        lines += [f"## [{mark}] {r.case_id}", "", f"Query: {r.query}", ""]
        if failed:
            lines += [f"Failed checks: {', '.join(failed)}", ""]
        lines += ["Answer:", "", r.answer.strip(), "", "Sources:", ""]
        lines += [
            f"- {s.get('title')} #{s.get('chunk_index')}: {s.get('preview', '')[:120]}" for s in r.sources
        ]
        lines.append("")
    return "\n".join(lines)


async def run(only: str | None) -> list[CaseResult]:
    cases = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    if only:
        cases = [c for c in cases if c["id"] == only]
    results: list[CaseResult] = []
    async with SessionLocal() as session:
        for case in cases:
            rag = await rag_answer(session, case["query"])
            result = CaseResult(case["id"], case["query"], rag["answer"], rag["sources"])
            result.checks = evaluate(case, rag["answer"], rag["sources"])
            results.append(result)
            print(f"{'PASS' if result.passed else 'FAIL'}  {case['id']}")
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="run a single case id")
    args = parser.parse_args()

    results = asyncio.run(run(args.only))
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = REPORT_DIR / f"{datetime.now(UTC):%Y%m%d-%H%M%S}.md"
    report.write_text(render_report(results), encoding="utf-8")
    print(f"Report: {report}")
    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
