"""Stage 6, evaluated against the released commit in a fresh read-only job."""

import argparse
import html
import re
import subprocess
from pathlib import Path

from common import Model, SHA, Stop, dump, git, load, markdown, objects, read_files, string, tracked
from sandbox import check

PRODUCT_FILES = re.compile(r"(?:src/|tests/|docs/)[A-Za-z0-9_./-]+|README\.(?:md|rst)|pyproject\.toml|LICENSE")


def neutral_text(text):
    return html.escape(text, quote=False).replace("@", "&#64;").replace("[", "&#91;").replace("`", "&#96;")


def review(repo, issue, base, head, round_number, model, directory, *, variant="rubric", checker=check):
    if not SHA.fullmatch(base) or not SHA.fullmatch(head):
        raise Stop("Review requires valid base and head SHAs.")
    if git(repo, "rev-parse", "HEAD").decode().strip() != head:
        raise Stop("Review checkout does not match the released head.")
    diff = git(repo, "diff", "--no-ext-diff", base, head).decode()
    if not diff or len(diff.encode()) > 90_000:
        raise Stop("The independent review needs a nonempty diff under 90 KB.")
    names = [name for name in tracked(repo) if PRODUCT_FILES.fullmatch(name)]
    changed = git(repo, "diff", "--name-only", "-z", base, head).decode().rstrip("\0").split("\0")
    inspection = model.ask("inspect", {"issue": issue, "diff": diff, "repository_index": names})
    paths = inspection.get("paths")
    run_tests = inspection.get("run_tests")
    if (not isinstance(paths, list) or len(paths) > 6 or type(run_tests) is not bool
            or any(not isinstance(path, str) or path not in names for path in paths)):
        raise Stop("Reviewer inspection requested an unsupported repository path or operation.")
    observed = {}
    if run_tests:
        for phase in ("build", "test"):
            result = checker(repo, phase)
            observed[phase] = {"exit": result["exit"], "output": result["log"][-4000:]}
            (directory / f"independent-{phase}.txt").write_text(result["log"], encoding="utf-8")
    files = read_files(repo, [*changed, *paths], limit=max(0, 22_000 - len(diff.encode())))
    line_numbers = {path: "\n".join(f"{i}: {line}" for i, line in enumerate(content.splitlines(), 1))
                    for path, content in files.items()}
    result = model.ask("review", {
        "issue": issue, "diff": diff, "head_files_with_line_numbers": line_numbers, "independent_checks": observed,
    }, extra="\n\nUse a terse review without a separate regression discussion."
        if variant == "short" else "")
    verdict = result.get("verdict")
    summary = string(result.get("summary"), "review summary", 2500)
    findings = objects(result.get("findings"), "review findings", maximum=6)
    if verdict not in {"approve", "request_changes"} or bool(findings) != (verdict == "request_changes"):
        raise Stop("The reviewer verdict conflicts with its blocking findings.")
    if verdict == "approve" and any(item["exit"] for item in observed.values()):
        raise Stop("The reviewer approved despite a failed independent check.")
    route = "done"
    lines = [f"**Verdict** {verdict.replace('_', ' ')}", "", f"Commit `{head}` · round {round_number}.",
             "", neutral_text(summary)]
    for finding in findings:
        path = string(finding.get("path"), "finding path", 170)
        if path not in names:
            raise Stop("A review finding names a file outside the checked-out product.")
        line = finding.get("line")
        selected = read_files(repo, [path])
        if type(line) is not int or path not in selected or not 1 <= line <= len(selected[path].splitlines()):
            raise Stop("A review finding requires a valid line at the released commit.")
        return_to = finding.get("return_to")
        if return_to not in {"design", "implementation"}:
            raise Stop("The reviewer must route a finding to design or implementation.")
        route = "design" if "design" in {route, return_to} else "implementation"
        lines.extend(["", f"- `{path}:{line}` · {return_to} — {neutral_text(string(finding.get('problem'), 'problem'))}"])
    if observed:
        lines.extend(["", "Independent checks run by the reviewer.",
                      *[f"- {phase} — exit {value['exit']}" for phase, value in observed.items()]])
    markdown(directory / "review.md", "Independent review", "\n".join(lines))
    dump(directory / "review.json", {"verdict": verdict, "return_to": route, "findings": findings,
                                      "head": head, "round": round_number})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--issue", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--round", type=int, required=True)
    parser.add_argument("--fixtures", type=Path)
    parser.add_argument("--variant", choices=["short", "rubric"], default="rubric")
    args = parser.parse_args()
    args.artifacts.mkdir(parents=True, exist_ok=True)
    try:
        review(args.repo.resolve(), load(args.issue), args.base, args.head, args.round,
               Model(args.artifacts, 2, args.fixtures), args.artifacts, variant=args.variant)
    except (Stop, OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        reason = str(error) if isinstance(error, Stop) else f"An input or tool failed ({type(error).__name__})."
        markdown(args.artifacts / "review.md", "Independent review", f"Stopped. {reason}")
        raise SystemExit(reason) from None


if __name__ == "__main__":
    main()
