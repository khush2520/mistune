"""Run both independent reviewer prompts against an actual seeded PR commit."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workflow"))

from common import Model, Stop, dump, git, load, markdown  # noqa: E402
from review import review  # noqa: E402

ISSUES = {"R1": "F1", "R2": "F1", "R3": "B1", "R4": "refactor", "R5": "refactor"}


def issue_for(case):
    issue = ISSUES[case]
    if issue == "refactor":
        return {"title": "Simplify CLI output branching", "body": "Use a guard clause while preserving file and stdout behavior."}
    title, body = (ROOT / "experiment" / "issues" / f"{issue}.md").read_text().split("\n\n", 1)
    return {"title": title.removeprefix("# "), "body": body.strip()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=ISSUES)
    parser.add_argument("repo", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    base = git(repo, "rev-parse", "HEAD^").decode().strip()
    issue = issue_for(args.case)
    summary = []
    for variant in ("rubric", "short"):
        directory = args.output / variant
        directory.mkdir(parents=True, exist_ok=True)
        model = Model(directory, 2)
        detail = ""
        try:
            review(repo, issue, base, head, 1, model, directory, variant=variant)
        except Stop as error:
            verdict = "invalid"
            detail = str(error)
            markdown(directory / "review.md", "Independent review", detail)
        else:
            verdict = load(directory / "review.json")["verdict"]
        summary.append({
            "case": args.case, "variant": variant, "head": head, "verdict": verdict,
            "detail": detail, "tokens": sum(row.get("total_tokens", 0) for row in model.history),
        })
    dump(args.output / "summary.json", summary)


if __name__ == "__main__":
    main()
