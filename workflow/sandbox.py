"""Run only the two fixed build/test commands in a clean, offline container."""

import json
import shutil
import subprocess
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory

from common import Stop
from run_checks import ROOT_FILES


def check(project, phase):
    with TemporaryDirectory(prefix="autose-source-") as folder:
        staged = Path(folder)
        staged.chmod(0o755)
        for name in ROOT_FILES:
            source = project / name
            target = staged / name
            if source.is_dir():
                shutil.copytree(source, target, symlinks=True, ignore=shutil.ignore_patterns("__pycache__"))
            elif source.is_file():
                shutil.copyfile(source, target)
        if any(path.is_symlink() for path in staged.rglob("*")):
            raise Stop("The candidate export contains a symbolic link.")
        return run_container(staged, phase)


def run_container(project, phase):
    name = "autose-" + uuid.uuid4().hex
    command = [
        "docker", "run", "--rm", "--name", name, "--network", "none",
        "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
        "--user", "65534:65534", "--pids-limit", "128", "--memory", "768m",
        "--cpus", "2", "--log-driver", "none",
        "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=256m",
        "--mount", f"type=bind,src={project},dst=/candidate,readonly",
        "autose-checks:local", phase,
    ]
    try:
        completed = subprocess.run(command, capture_output=True, timeout=150)
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=10, check=False)
        raise Stop(f"The {phase} container timed out.") from None
    if completed.returncode:
        raise Stop(f"The {phase} container failed to return a check result.")
    try:
        return json.loads(completed.stdout)
    except (ValueError, UnicodeDecodeError):
        raise Stop(f"The {phase} container returned a malformed check result.") from None
