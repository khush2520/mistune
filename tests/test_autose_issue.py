import os
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


def test_ac_01_cli_1(tmp_path):
    reference = invoke(['-m', 'hello'], tmp_path)
    assert reference.returncode == 0
    assert reference.stdout
    result = invoke(['-m', 'hello', '--output', '-'], tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout == reference.stdout

def test_ac_02_cli_2(tmp_path):
    reference = invoke(['-m', 'hello'], tmp_path)
    assert reference.returncode == 0
    assert reference.stdout
    result = invoke(['-m', 'hello', '-o', '-'], tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout == reference.stdout

def test_ac_03_cli_3(tmp_path):
    target = tmp_path / 'output.md'
    result = invoke(['-m', 'hello', '--output', 'output.md'], tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout == ''
    assert target.read_text(encoding='utf-8') == __import__('mistune').html('hello')

def test_ac_04_cli_4(tmp_path):
    target = tmp_path / 'existing-'
    target.write_text('unchanged sentinel\n', encoding='utf-8')
    reference = invoke(['-m', 'hello'], tmp_path)
    assert reference.returncode == 0
    assert reference.stdout
    result = invoke(['-m', 'hello', '--output', '-'], tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout == reference.stdout
    assert target.read_text(encoding='utf-8') == 'unchanged sentinel\n'
