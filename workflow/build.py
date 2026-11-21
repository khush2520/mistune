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
from cli_cases import compile_cases
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
    data["context"] = [name for name in dict.fromkeys(context) if name in project_files][:4]
    markdown(directory / "design.md", "Design", "\n".join([
        approach, "", "## Architecture fit", "", fit, "", "## File and symbol plan", "",
        *lines, "", "## Test approach", "", checks,
    ]))
    dump(directory / "design.json", data)
    return allowed


def line_replacements(repo, edits, pattern, allowed):
    grouped = {}
    for edit in objects(edits, "line edits", maximum=8):
        name = string(edit.get("path"), "edit path", 150)
        if not pattern.fullmatch(name) or (allowed is not None and name not in allowed):
            raise Stop("A model proposed an edit outside this stage's allowlist.")
        start, end, replacement = edit.get("start"), edit.get("end"), edit.get("replacement")
        if type(start) is not int or type(end) is not int or not isinstance(replacement, str):
            raise Stop(f"A line edit in {name} needs integer bounds and replacement text.")
        grouped.setdefault(name, []).append((start, end, replacement))
    files = {}
    for name, changes in grouped.items():
        path = safe_path(repo, name)
        if not path.is_file():
            if len(changes) != 1 or changes[0][:2] != (0, 0):
                raise Stop(f"A new file needs one edit with start and end set to zero: {name}.")
            files[name] = changes[0][2]
            continue
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        next_start = len(lines) + 1
        for start, end, replacement in sorted(changes, reverse=True):
            if not 1 <= start <= end < next_start:
                raise Stop(f"Line range {start} through {end} overlaps or is outside {name}.")
            lines[start - 1:end] = [replacement.rstrip("\n") + "\n"] if replacement else []
            next_start = start
        files[name] = "".join(lines)
    return files


def condition_replacements(repo, edits, pattern, allowed):
    files = {}
    for edit in objects(edits, "condition edits", maximum=8):
        name = string(edit.get("path"), "edit path", 150)
        if not pattern.fullmatch(name) or (allowed is not None and name not in allowed):
            raise Stop("A model proposed a condition outside this stage's allowlist.")
        path = safe_path(repo, name)
        original = files.get(name)
        if original is None:
            original = path.read_text(encoding="utf-8")
        expression = string(edit.get("expression"), "if expression", 400)
        if "\n" in expression or "\r" in expression:
            raise Stop("A replacement condition must be a single-line Python expression.")
        try:
            ast.parse(expression, mode="eval")
        except SyntaxError:
            raise Stop("A replacement condition must be a valid Python expression.") from None
        matches = [node.test for node in ast.walk(ast.parse(original))
                   if isinstance(node, ast.If) and (
                       ast.get_source_segment(original, node.test) == edit["condition"]
                       if "condition" in edit else node.lineno == edit.get("line"))]
        if len(matches) != 1 or matches[0].lineno != matches[0].end_lineno:
            raise Stop(f"Expected exactly one matching single-line if condition in {name}.")
        test = matches[0]
        lines = original.splitlines(keepends=True)
        line = lines[test.lineno - 1].encode()
        replacement = line[:test.col_offset] + expression.encode() + line[test.end_col_offset:]
        lines[test.lineno - 1] = replacement.decode()
        files[name] = "".join(lines)
    return files


def apply_files(repo, result, pattern, allowed=None):
    files = result.get("files")
    if "condition_edits" in result:
        files = condition_replacements(repo, result["condition_edits"], pattern, allowed)
    elif "line_edits" in result:
        files = line_replacements(repo, result["line_edits"], pattern, allowed)
    elif "edits" in result:
        files = {}
        for edit in objects(result["edits"], "edits", maximum=8):
            name = string(edit.get("path"), "edit path", 150)
            if not pattern.fullmatch(name) or (allowed is not None and name not in allowed):
                raise Stop("A model proposed an edit outside this stage's allowlist.")
            target = safe_path(repo, name)
            old, new = edit.get("old"), edit.get("new")
            if not isinstance(old, str) or not isinstance(new, str):
                raise Stop("Each edit needs old and new text.")
            if name in files:
                current = files[name]
            elif target.is_file():
                current = target.read_text(encoding="utf-8")
            else:
                current = ""
            if old:
                if current.count(old) != 1:
                    raise Stop(f"Replacement text for {name} must match exactly once.")
                files[name] = current.replace(old, new, 1)
            elif current or target.exists():
                raise Stop(f"An empty edit anchor cannot replace existing file {name}.")
            else:
                files[name] = new
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
    for name, content in files.items():
        target = safe_path(repo, name)
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


def issue_source_matches(repo, issue, paths):
    text = str(issue.get("title", "")) + "\n" + str(issue.get("body", ""))
    flags = re.findall(r"(?<![\w-])--[a-z][a-z0-9-]+", text)
    references = re.findall(r"`((?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*)`", text)
    arguments = ["args." + flag[2:].replace("-", "_") for flag in flags]
    terms = list(dict.fromkeys([*flags, *arguments, *(name.rsplit(".", 1)[-1] for name in references)]))[:8]
    matches = {}
    for name in paths:
        source = safe_path(repo, name).read_text(encoding="utf-8")
        lines = [(i, line.strip()) for i, line in enumerate(source.splitlines(), 1)
                 if any(term in line for term in terms)]
        if lines:
            functions = [node for node in ast.walk(ast.parse(source))
                         if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
            functions.sort(key=lambda node: node.end_lineno - node.lineno)
            matches[name] = []
            for number, line in lines[:6]:
                owner = next((node.name for node in functions if node.lineno <= number <= node.end_lineno), "module")
                matches[name].append(f"{number} ({owner}): {line}")
        if len(matches) == 6:
            break
    return matches


def architecture_context(repo):
    architecture = (repo / "ARCHITECTURE.md").read_text(encoding="utf-8")
    overview = architecture.split("## 2. Architecture", 1)[0]
    constraints = architecture.split("## 3. Constraints", 1)[1]
    return overview + "\n## 3. Constraints" + constraints


def a1_rules():
    skill = (HERE / "prompts/a1-skill.md").read_text(encoding="utf-8")
    acceptance = skill.split("### 3.3 Testability", 1)[1].split("## 4.", 1)[0]
    validation = skill.split("## 6. Verification", 1)[1].split("## 7.", 1)[0]
    return "\n\n## A1 acceptance criteria" + acceptance + "\n\n## A1 verification" + validation


def run(repo, directory, issue, model, *, previous=None, review=None, checker=check):
    stage = "Requirements"
    try:
        spec = load(previous / "spec.json") if previous is not None else model.ask(
            "requirements", {"issue": issue},
            extra=a1_rules(),
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
                "architecture": architecture_context(repo),
                "issue_source_matches": issue_source_matches(repo, issue, index),
                "source_index": {path: names[:14] for path, names in index.items()},
            })
        allowed = design(plan, repo, index, directory)
        feedback = ""
        cli_extra = ""
        if "src/mistune/__main__.py" in allowed:
            cli_extra = "\n\n" + (HERE / "prompts/cli-testing.md").read_text(encoding="utf-8")
        for attempt in (1, 2):
            stage = "Implementation"
            try:
                source = read_files(repo, [*sorted(allowed), *plan["context"]], limit=26_000)
                if any((repo / path).exists() and path not in source for path in allowed):
                    raise Stop("A target file exceeded the implementation context limit.")
                single_condition = None
                if len(plan["targets"]) == 1:
                    target = plan["targets"][0]
                    tree = ast.parse(source[target["path"]])
                    function = next((node for node in tree.body if isinstance(node, ast.FunctionDef)
                                     and node.name == target["symbol"]), None)
                    conditions = [node for node in function.body if isinstance(node, ast.If)] if function else []
                    if len(conditions) == 1:
                        single_condition = {
                            "path": target["path"], "line": conditions[0].lineno,
                            "condition": ast.get_source_segment(source[target["path"]], conditions[0].test),
                        }
                implementation_data = {
                    "issue": issue, "spec": spec, "design": plan, "current_files": {
                        name: "\n".join(f"{number}: {line}" for number, line in enumerate(content.splitlines(), 1))
                        for name, content in source.items()
                    },
                    "previous_failure": feedback, "review_feedback": review,
                }
                if single_condition:
                    result = model.ask("condition", {
                        "issue": issue, "function": ast.get_source_segment(source[target["path"]], function),
                        "current_condition": single_condition["condition"], "previous_failure": feedback,
                    })
                else:
                    result = model.ask("implementation", implementation_data)
                dump(directory / f"implementation-{attempt}.json", result)
                if "expression" in result and single_condition:
                    result = {"condition_edits": [{**single_condition, "expression": result["expression"]}]}
                apply_files(repo, result, SOURCE, allowed)
                for target in plan["targets"]:
                    path = repo / target["path"]
                    if not path.is_file() or target["symbol"] not in symbols(path):
                        raise Stop(f"The patch is missing the planned symbol {target['symbol']} in {target['path']}.")
                patch = git(repo, "diff", "--cached", "--binary", "HEAD")
                (directory / "diff.patch").write_bytes(patch)
                build = checker(repo, "build")
                (directory / f"build-{attempt}.txt").write_text(build["log"], encoding="utf-8")
                if build["exit"]:
                    raise Stop(f"The wheel build failed (exit {build['exit']}).")
                stage = "Testing"
                test_names = [p.relative_to(repo).as_posix() for p in (repo / "tests").glob("test_autose_*.py")]
                testing_data = {
                    "issue": issue, "spec": spec, "design": plan, "previous_failure": feedback,
                    "current_sources": read_files(repo, sorted(allowed), limit=21_000),
                    "current_tests": read_files(repo, test_names, limit=12_000),
                }
                if cli_extra:
                    result = model.ask("cli-testing", {
                        "issue": issue, "criterion_ids": criteria, "previous_failure": feedback,
                        "candidate_source": testing_data["current_sources"],
                    })
                else:
                    result = model.ask("testing", testing_data)
                dump(directory / f"testing-{attempt}.json", result)
                if "cli_cases" in result:
                    result = {"files": {"tests/test_autose_issue.py": compile_cases(result["cli_cases"], criteria)}}
                elif "test_code" in result:
                    result = {"files": {"tests/test_autose_issue.py": result["test_code"]}}
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
