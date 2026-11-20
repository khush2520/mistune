"""Stages 1–4, with explicit gates and one implementation retry per round."""

import argparse
import ast
import re
import subprocess
from pathlib import Path

from common import (
    HERE, MAX_FILE_BYTES, SOURCE, TEST, Model, Stop, dump, git, load, markdown,
    objects, read_files, safe_path, string, symbols, tracked,
)
from sandbox import check

AC = re.compile(r"AC-\d{2}")
REQUIREMENT = re.compile(r"(?:FR|NFR)-\d{2}")
PY_NAME = re.compile(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)?", re.ASCII)
CHECKS = {"completeness", "consistency", "traceability", "feasibility", "testability"}
ARTIFACTS = {
    "Requirements": "spec.md", "Design": "design.md",
    "Implementation": "diff.patch", "Testing": "test_report.md",
}


def list_of_strings(data, key):
    entries = data.get(key)
    if not isinstance(entries, list) or len(entries) > 12:
        raise Stop(f"The {key} field needs a list of at most 12 items.")
    return [string(item, key) for item in entries]


def requirements(data, directory):
    status = data.get("status")
    if status not in {"ready", "blocked"}:
        raise Stop("Requirements must declare ready or blocked.")
    overview = string(data.get("summary"), "summary")
    details = []
    for key in ("actors", "constraints", "assumptions", "questions"):
        entries = list_of_strings(data, key)
        details.extend([f"## {key.title()}", *[f"- {entry}" for entry in entries], ""])
    criteria = {}
    for entry in objects(data.get("criteria"), "criteria", maximum=8):
        code = string(entry.get("id"), "acceptance criterion", 5)
        requirement = string(entry.get("requirement"), "requirement ID", 6)
        if not AC.fullmatch(code) or not REQUIREMENT.fullmatch(requirement) or code in criteria:
            raise Stop("Acceptance criteria require unique AC IDs and FR/NFR IDs.")
        provenance = entry.get("provenance")
        if provenance not in {"confirmed", "inferred"}:
            raise Stop("Each criterion needs provenance.")
        fields = {key: string(entry.get(key), key) for key in ("evidence", "given", "when", "then")}
        if re.fullmatch(r"(?:works|good|fast|better|correct|as expected|improved)[. ]*", fields["then"], re.I):
            raise Stop(f"{code} has no observable expected outcome.")
        criteria[code] = {**fields, "requirement": requirement, "provenance": provenance}
    details.append("## Acceptance criteria")
    for code, fields in criteria.items():
        details.append(f"\n### {code} ({fields['requirement']}, {fields['provenance']})")
        details.extend(f"- **{key.title()}** {fields[key]}" for key in ("evidence", "given", "when", "then"))
    checks = data.get("checks")
    if not isinstance(checks, dict) or set(checks) != CHECKS or not all(type(v) is bool for v in checks.values()):
        raise Stop("The validation summary needs all five A1 boolean checks.")
    details.extend(["\n## A1 validation", *[f"- {key} — {'pass' if checks[key] else 'unresolved'}"
                                              for key in sorted(checks)]])
    markdown(directory / "spec.md", "Requirements", f"{overview}\n\n" + "\n".join(details))
    if status != "ready" or data["questions"] or not criteria or not all(checks.values()):
        raise Stop("Clarification or a testable specification is needed before design.")
    dump(directory / "spec.json", data)
    return list(criteria)


def design(data, repo, index, directory):
    approach = string(data.get("approach"), "approach")
    fit = string(data.get("architecture_fit"), "architecture fit")
    checks = string(data.get("tests"), "test approach")
    targets = objects(data.get("targets"), "targets", minimum=1)
    lines = []
    allowed = set()
    for entry in targets:
        path = string(entry.get("path"), "target path", 150)
        symbol = string(entry.get("symbol"), "target symbol", 150)
        action = entry.get("action")
        change = string(entry.get("change"), "planned change")
        if not SOURCE.fullmatch(path) or not PY_NAME.fullmatch(symbol):
            raise Stop("Design targets must name an allowed source file and a Python symbol.")
        safe_path(repo, path)
        existing = symbol in index.get(path, [])
        if action not in {"edit", "add"} or (action == "edit") != existing:
            raise Stop(f"The declared {action!r} symbol {path}:{symbol} disagrees with the source index.")
        allowed.add(path)
        lines.append(f"- `{path}` · `{symbol}` ({action}) — {change}")
    context = list_of_strings(data, "context")
    project_files = {name for name in tracked(repo) if name.startswith(("src/mistune/", "tests/"))}
    if len(context) > 4 or any(name not in project_files for name in context):
        raise Stop("Design context must name at most four tracked files.")
    read_files(repo, context)
    markdown(directory / "design.md", "Design", "\n".join([
        approach, "", "## Architecture fit", "", fit, "", "## File and symbol plan", "",
        *lines, "", "## Test approach", "", checks,
    ]))
    dump(directory / "design.json", data)
    return allowed


def apply_files(repo, result, pattern, allowed=None):
    files = result.get("files")
    if not isinstance(files, dict) or len(files) > 8:
        raise Stop("The files response needs an object with at most eight file entries.")
    for name, content in files.items():
        if not pattern.fullmatch(name) or (allowed is not None and name not in allowed):
            raise Stop("A model proposed a file outside this stage's allowlist.")
        target = safe_path(repo, name)
        if not isinstance(content, str) or len(content.encode()) > MAX_FILE_BYTES or "\0" in content:
            raise Stop("A proposed Python file exceeded its permitted content size.")
        try:
            ast.parse(content)
        except SyntaxError as error:
            raise Stop(f"Proposed file {name} does not parse on line {error.lineno}.") from None
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content.rstrip("\n") + "\n", encoding="utf-8")
    if files:
        git(repo, "add", "--", *files)


def mapped_tests(repo, criteria):
    tests = {}
    for path in sorted((repo / "tests").glob("test_autose_*.py")):
        for node in ast.parse(path.read_text(encoding="utf-8")).body:
            if isinstance(node, ast.FunctionDef) and re.fullmatch(r"test_ac_\d{2}(?:_\w+)?", node.name):
                criterion = "AC-" + node.name.split("_")[2]
                tests.setdefault(criterion, set()).add((path.stem, node.name))
    missing = set(criteria) - tests.keys()
    if missing:
        raise Stop(f"Missing test definitions for {', '.join(sorted(missing))}.")
    return {criterion: tests[criterion] for criterion in criteria}


def confirm_results(report, mapping):
    if report["exit"] or not report["collected"]:
        raise Stop(f"The full suite failed or collected no tests (exit {report['exit']}).")
    passed = {(case["module"], case["name"]) for case in report["cases"] if case["passed"]}
    did_not_pass = {(case["module"], case["name"]) for case in report["cases"] if not case["passed"]}
    missing = [criterion for criterion, tests in mapping.items() if not tests & (passed - did_not_pass)]
    if missing:
        raise Stop(f"No executed passing test for {', '.join(missing)}.")


def stage_error(directory, stage, reason):
    path = directory / ARTIFACTS[stage]
    prior = path.read_text(encoding="utf-8") if path.exists() else ""
    if stage == "Implementation":
        prior = f"# Build failed: {reason}\n" + prior
    else:
        prior = (prior or f"# {stage}\n") + f"\n\n## Stopped\n\n{reason}\n"
    path.write_text(prior, encoding="utf-8")
    dump(directory / "build_status.json", {"status": "failed", "stage": stage, "reason": reason})


def run(repo, directory, issue, model, *, previous=None, review=None, checker=check):
    stage = "Requirements"
    try:
        spec = load(previous / "spec.json") if previous is not None else model.ask(
            "requirements", {"issue": issue},
            extra="\n\n# Original A1 skill\n\n" + (HERE / "prompts/a1-skill.md").read_text(),
        )
        criteria = requirements(spec, directory)
        stage = "Design"
        index = {name: symbols(repo / name) for name in tracked(repo) if SOURCE.fullmatch(name)}
        if previous is not None and review["return_to"] == "implementation":
            plan = load(previous / "design.json")
            # An added symbol from round one is now an edit target in round two.
            for target in plan["targets"]:
                if target["symbol"] in index.get(target["path"], []):
                    target["action"] = "edit"
        else:
            plan = model.ask("design", {
                "issue": issue, "spec": spec, "review_feedback": review,
                "architecture": (repo / "ARCHITECTURE.md").read_text(), "source_index": index,
            })
        allowed = design(plan, repo, index, directory)
        feedback = ""
        for attempt in (1, 2):
            stage = "Implementation"
            try:
                source = read_files(repo, [*sorted(allowed), *plan["context"]])
                if any((repo / path).exists() and path not in source for path in allowed):
                    raise Stop("A target file exceeded the implementation context limit.")
                result = model.ask("implementation", {
                    "spec": spec, "design": plan, "current_files": source,
                    "previous_failure": feedback, "review_feedback": review,
                })
                apply_files(repo, result, SOURCE, allowed)
                patch = git(repo, "diff", "--cached", "--binary", "HEAD")
                (directory / "diff.patch").write_bytes(patch)
                build = checker(repo, "build")
                (directory / f"build-{attempt}.txt").write_text(build["log"], encoding="utf-8")
                if build["exit"]:
                    raise Stop(f"The wheel build failed (exit {build['exit']}).")
                stage = "Testing"
                test_names = [p.relative_to(repo).as_posix() for p in (repo / "tests").glob("test_autose_*.py")]
                result = model.ask("testing", {
                    "spec": spec, "design": plan, "previous_failure": feedback,
                    "current_sources": read_files(repo, sorted(allowed), limit=62_000),
                    "current_tests": read_files(repo, test_names, limit=12_000),
                })
                apply_files(repo, result, TEST)
                mapping = mapped_tests(repo, criteria)
                report = checker(repo, "test")
                (directory / f"pytest-{attempt}.txt").write_text(report["log"], encoding="utf-8")
                confirm_results(report, mapping)
                patch = git(repo, "diff", "--cached", "--binary", "HEAD")
                if not patch or len(patch) > 75_000:
                    raise Stop("The candidate needs a nonempty patch within 75 KB.")
                (directory / "diff.patch").write_bytes(patch)
                cases = [f"- {criterion} — " + ", ".join(f"`{module}::{name}`" for module, name in sorted(tests))
                         for criterion, tests in mapping.items()]
                markdown(directory / "test_report.md", "Testing", "\n".join([
                    f"Full suite passed on attempt {attempt}; {report['collected']} JUnit cases recorded.",
                    "Each acceptance criterion had an executed passing case.", "", *cases,
                ]))
                dump(directory / "build_status.json", {"status": "passed", "attempt": attempt})
                return
            except Stop as error:
                feedback = str(error)
                logfile = directory / (f"build-{attempt}.txt" if stage == "Implementation" else f"pytest-{attempt}.txt")
                if logfile.exists():
                    feedback += "\n" + logfile.read_text(encoding="utf-8")[-6000:]
                markdown(directory / f"attempt-{attempt}.md", f"{stage} gate", str(error))
                if attempt == 2:
                    raise
    except (Stop, OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        reason = str(error) if isinstance(error, Stop) else f"An input or tool failed ({type(error).__name__})."
        stage_error(directory, stage, reason)
        raise Stop(reason) from None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--issue", type=Path, required=True)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--fixtures", type=Path)
    args = parser.parse_args()
    if bool(args.previous) != bool(args.review):
        parser.error("--previous and --review must be provided together")
    args.artifacts.mkdir(parents=True, exist_ok=True)
    try:
        run(args.repo.resolve(), args.artifacts, load(args.issue),
            Model(args.artifacts, 6, args.fixtures), previous=args.previous,
            review=load(args.review) if args.review else None)
    except Stop as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()
