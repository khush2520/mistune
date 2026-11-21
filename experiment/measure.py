"""Run local decision probes without an API key. These use authored responses."""

import csv
import json
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workflow"))

from build import CHECKS, confirm_results, mapped_tests, run  # noqa: E402
from common import Model, Stop, dump, git  # noqa: E402
from github_flow import certify_diff  # noqa: E402
from review import review  # noqa: E402
from sandbox import check  # noqa: E402

CLI = "src/mistune/__main__.py"
CI_TEST = "tests/test_autose_probe.py"
FIELDS = ["kind", "case", "variant", "expected", "observed", "detail", "junit_cases", "tokens"]


def row(kind, case, variant, expected, observed, detail="", collected=""):
    return dict(zip(FIELDS, (kind, case, variant, expected, observed, detail, collected, 0)))


def fixture_checkout(root):
    repo = root / "candidate"
    git(root, "clone", "--quiet", "--no-local", str(ROOT), str(repo))
    git(repo, "switch", "--quiet", "--detach", "HEAD")
    return repo.resolve()


def gate_experiment(repo, evidence):
    probes = {
        "passing": "def test_ac_01():\n    assert 1 + 1 == 2\n",
        "skipped": 'import pytest\n\n@pytest.mark.skip(reason="probe")\ndef test_ac_01():\n    assert True\n',
        "failed": "def test_ac_01():\n    assert 1 + 1 == 3\n",
        "uncollected": 'def test_ac_01(unknown_fixture):\n    assert True\ntest_ac_01.__test__ = False\n',
        "missing": "def test_other():\n    assert True\n",
    }
    test_file = repo / CI_TEST
    results = []
    for case, content in probes.items():
        expected = "pass" if case == "passing" else "stop"
        test_file.write_text(content, encoding="utf-8")
        try:
            mapping = mapped_tests(repo, ["AC-01"])
        except Stop as error:
            mapping = None
            static_reason = str(error)
        else:
            static_reason = "Found a function named for AC-01."
        results.append(row("D7", case, "definition-only", expected,
                           "pass" if mapping else "stop", static_reason))
        report = check(repo, "test")
        dump(evidence / f"D7-{case}.json", report)
        try:
            if mapping is None:
                raise Stop(static_reason)
            confirm_results(report, mapping)
        except Stop as error:
            state, reason = "stop", str(error)
        else:
            state, reason = "pass", "AC-01 executed and passed."
        results.append(row("D7", case, "executed-case-gate", expected, state, reason, report["collected"]))
    test_file.unlink()
    return results


def issue_message(case):
    filename = ROOT / "experiment" / "issues" / f"{case}.md"
    if case == "F1":
        filename = ROOT / "experiment" / "historical_issues" / filename.name
    if filename.exists():
        title, body = filename.read_text().split("\n\n", 1)
        return {"number": 1, "title": title.removeprefix("# "), "body": body.strip()}
    return {"number": 1, "title": "Simplify CLI output branching",
            "body": "Use a guard clause while preserving file and stdout behavior."}


def authored_replies(directory, repo, *, vague):
    answers = directory / "answers"
    answers.mkdir()
    issue_id = "V1" if vague else "F1"
    criteria = [
        {"id": "AC-01", "requirement": "FR-01", "provenance": "confirmed", "evidence": "Issue output flags",
         "given": "A file named dash exists", "when": "Render to --output -",
         "then": "Send the usual HTML to stdout and preserve the file named dash."},
    ] if not vague else []
    dump(answers / "01-requirements.json", {
        "status": "blocked" if vague else "ready", "summary": issue_message(issue_id)["title"],
        "actors": ["CLI user" if not vague else "Documentation author"], "constraints": [], "assumptions": [],
        "questions": ["What Markdown input shows the problem?", "What output should that input produce?"]
        if vague else [], "criteria": criteria,
        "checks": {key: not vague for key in CHECKS},
    })
    if vague:
        return answers
    dump(answers / "02-design.json", {
        "approach": "Reuse the existing stdout branch when the output flag is a dash.",
        "architecture_fit": "Keep the CLI dispatcher in __main__.py. Leave parsers and renderers alone.",
        "tests": "Use a CLI subprocess with a pre-existing dash file.",
        "targets": [{"path": CLI, "symbol": "_output", "action": "edit", "change": "Use stdout for a dash."}],
        "context": ["tests/test_cli.py"],
    })
    source = (repo / CLI).read_text()
    replacement = source.replace("if args.output:", 'if args.output and args.output != "-":', 1)
    tests = (
        "import subprocess\nimport sys\nfrom pathlib import Path\n\n\n"
        "def test_ac_01(tmp_path, monkeypatch):\n"
        '    dash = tmp_path / "-"\n    dash.write_text("keep")\n'
        '    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).resolve().parents[1] / "src"))\n'
        '    command = [sys.executable, "-m", "mistune", "-m", "Hi", "--output", "-"]\n'
        "    result = subprocess.run(command, cwd=tmp_path, text=True, capture_output=True, check=True)\n"
        '    assert result.stdout == "<p>Hi</p>\\n\\n"\n    assert dash.read_text() == "keep"\n'
    )
    dump(answers / "03-implementation.json", {"files": {CLI: source}})
    dump(answers / "04-testing.json", {"files": {CI_TEST: tests}})
    dump(answers / "05-implementation.json", {"files": {CLI: replacement}})
    dump(answers / "06-testing.json", {"files": {}})
    return answers


def workflow_probes(repo, root):
    vague = root / "vague"
    vague.mkdir()
    try:
        run(repo, vague, issue_message("V1"), Model(vague, 6, authored_replies(vague, repo, vague=True)))
    except Stop:
        pass
    status = json.loads((vague / "build_status.json").read_text())
    assert status["stage"] == "Requirements"
    shutil.rmtree(vague / "answers")

    directory = root / "scripted-run"
    directory.mkdir()
    answers = authored_replies(directory, repo, vague=False)
    base = git(repo, "rev-parse", "HEAD").decode().strip()
    run(repo, directory, issue_message("F1"), Model(directory, 6, answers))
    assert (directory / "attempt-1.md").exists()
    certify_diff(repo, base)
    git(repo, "-c", "user.name=AutoSE fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "Scripted local F1 candidate")
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    review_dir = directory / "review"
    review_dir.mkdir()
    dump(answers / "01-inspect.json", {"paths": [], "run_tests": True})
    dump(answers / "02-review.json", {"verdict": "approve", "summary": "The dash case uses stdout and leaves the file alone.",
                                     "findings": []})
    review(repo, issue_message("F1"), base, head, 1, Model(review_dir, 2, answers), review_dir)
    shutil.rmtree(answers)
    git(repo, "switch", "--quiet", "--detach", base)
    return [
        row("workflow", "V1", "scripted", "Requirements stop", "Requirements stop", status["reason"]),
        row("workflow", "F1", "scripted", "retry then review", "retry then review",
            "First test failed; implementation retry and independent suite passed."),
    ]


def review_experiment(repo, root):
    results = []
    base = git(repo, "rev-parse", "HEAD").decode().strip()
    fixtures = ROOT / "experiment" / "seeded_prs"
    response_by_case = {
        "R1": {"verdict": "approve", "summary": "Output routing is unchanged for other file paths.", "findings": []},
        "R2": {"verdict": "approve", "summary": "The requested output is printed.",
               "findings": [{"path": CLI, "line": 34, "problem": "The dash path is also opened for writing.",
                             "return_to": "implementation"}]},
        "R3": {"verdict": "request_changes", "summary": "An unrelated CLI case regressed.",
               "findings": [{"path": CLI, "line": 9999, "problem": "Empty stdin now succeeds.",
                             "return_to": "implementation"}]},
        "R4": {"verdict": "approve", "summary": "The guard clause preserves both code paths.", "findings": []},
        "R5": {"verdict": "request_changes", "summary": "The caller's output path is ignored.", "findings": []},
    }
    with (fixtures / "labels.csv").open(newline="") as stream:
        labels = list(csv.DictReader(stream))
    for label in labels:
        case = label["case"]
        directory = root / case
        directory.mkdir()
        git(repo, "apply", "--index", str(fixtures / f"{case}.patch"))
        git(repo, "-c", "user.name=AutoSE fixture", "-c", "user.email=fixture@example.invalid",
            "commit", "-qm", f"Seeded review {case}")
        head = git(repo, "rev-parse", "HEAD").decode().strip()
        dump(directory / "01-inspect.json", {"paths": [], "run_tests": False})
        response = response_by_case[case]
        dump(directory / "02-review.json", response)
        results.append(row("D8", case, "verdict-only", label["expected"], response["verdict"]))
        try:
            review(repo, issue_message(label["issue"]), base, head, 1, Model(directory, 2, directory), directory)
        except Stop as error:
            results.append(row("D8", case, "evidence-gate", label["expected"], "stop", str(error)))
        else:
            results.append(row("D8", case, "evidence-gate", label["expected"], response["verdict"]))
        git(repo, "switch", "--quiet", "--detach", base)
    return results


def main(output):
    output.mkdir(parents=True, exist_ok=True)
    evidence = output / "local"
    evidence.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="autose-experiment-") as area:
        repo = fixture_checkout(Path(area))
        baseline = {phase: check(repo, phase) for phase in ("build", "test")}
        for phase, value in baseline.items():
            dump(evidence / f"baseline-{phase}.json", value)
            if value["exit"]:
                raise SystemExit(f"Baseline {phase} failed. See {evidence}.")
        results = [row("baseline", "mistune", "offline-container", "pass", "pass",
                       "Wheel and full pinned suite passed.", baseline["test"]["collected"])]
        results.extend(gate_experiment(repo, evidence))
        results.extend(workflow_probes(repo, evidence))
        results.extend(review_experiment(repo, evidence))
    with (output / "results.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
