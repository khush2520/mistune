"""Compile the test writer's declarative Mistune CLI cases into pytest."""

import re

from common import Stop, objects


PREAMBLE = '''import os
from pathlib import Path
import subprocess
import sys


SOURCE = Path(__file__).resolve().parents[1] / "src"


def invoke(args, cwd):
    return subprocess.run(
        [sys.executable, "-m", "mistune", *args], cwd=cwd,
        env={**os.environ, "PYTHONPATH": str(SOURCE)},
        input="", capture_output=True, encoding="utf-8", timeout=10,
    )
'''


def arguments(value):
    if not isinstance(value, list) or len(value) > 20 or any(
        not isinstance(arg, str) or len(arg) > 1000 or "\0" in arg for arg in value
    ):
        raise Stop("A CLI test needs an args list of at most 20 short strings.")
    return value


def file_checks(lines, case):
    file = case.get("file")
    if not isinstance(file, dict):
        raise Stop("A CLI file check must be an object.")
    name = file.get("name")
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9-][A-Za-z0-9_.-]{0,79}", name):
        raise Stop("A CLI file check must name a file in the test directory.")
    lines.append(f"    target = tmp_path / {name!r}")
    if "before" in file:
        before = file["before"]
        if not isinstance(before, str) or len(before) > 3000:
            raise Stop("The initial test file contents must be a short string.")
        lines.append(f"    target.write_text({before!r}, encoding='utf-8')")
    after = file.get("after")
    if after is None:
        return "    assert not target.exists()"
    if not isinstance(after, str) or len(after) > 3000:
        raise Stop("The expected test file contents must be a short string or null.")
    return f"    assert target.read_text(encoding='utf-8') == {after!r}"


def compile_cases(data, criteria):
    sections = [PREAMBLE]
    for number, case in enumerate(objects(data, "CLI test cases", minimum=1, maximum=12), 1):
        criterion = case.get("id")
        if criterion not in criteria:
            raise Stop("Each CLI test needs an acceptance criterion ID from the spec.")
        comparisons = {"stdout", "same_stdout_as"} & case.keys()
        if len(comparisons) > 1 or (not comparisons and "file" not in case):
            raise Stop("A CLI case needs one stdout expectation, a file expectation, or both.")
        lines = [f"def test_ac_{criterion[-2:]}_cli_{number}(tmp_path):"]
        check_file = file_checks(lines, case) if "file" in case else None
        if "same_stdout_as" in case:
            reference = arguments(case["same_stdout_as"])
            if reference == case.get("args"):
                raise Stop("Reference and candidate CLI arguments must differ.")
            lines.extend([f"    reference = invoke({reference!r}, tmp_path)",
                          "    assert reference.returncode == 0", "    assert reference.stdout"])
        command = arguments(case.get("args"))
        lines.extend([f"    result = invoke({command!r}, tmp_path)", "    assert result.returncode == 0, result.stderr"])
        if "stdout" in case:
            stdout = case["stdout"]
            if not isinstance(stdout, str) or len(stdout) > 3000:
                raise Stop("Expected stdout must be a short string.")
            lines.append(f"    assert result.stdout == {stdout!r}")
        if "same_stdout_as" in case:
            lines.append("    assert result.stdout == reference.stdout")
        if check_file:
            lines.append(check_file)
        sections.append("\n".join(lines))
    return "\n\n".join(sections) + "\n"
