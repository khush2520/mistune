"""Entrypoint in the credential-free container, also usable on trusted local fixtures."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree

ROOT_FILES = ("src", "tests", "pyproject.toml", "README.rst", "setup.py", "MANIFEST.in", "LICENSE")


def execution(phase, source):
    with TemporaryDirectory(dir="/tmp") as area:
        root = Path(area)
        for name in ROOT_FILES:
            target = source / name
            if target.is_dir():
                shutil.copytree(target, root / name, ignore=shutil.ignore_patterns("__pycache__"))
            elif target.is_file():
                shutil.copyfile(target, root / name)
        commands = {
            "build": ["-m", "pip", "wheel", "--no-build-isolation", "--no-deps", "--no-index",
                      ".", "--wheel-dir", str(root / "wheel")],
            "test": ["-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=short",
                     "--junitxml", str(root / "results.xml"), "tests"],
        }
        logfile = root / "process.log"
        environment = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PIP_DISABLE_PIP_VERSION_CHECK="1")
        with logfile.open("wb") as log:
            try:
                status = subprocess.run(
                    [sys.executable, *commands[phase]], cwd=root, env=environment,
                    stdout=log, stderr=subprocess.STDOUT, timeout=120,
                ).returncode
            except subprocess.TimeoutExpired:
                status = 124
        with logfile.open("rb") as log:
            log.seek(max(0, logfile.stat().st_size - 8000))
            tail = log.read().decode(errors="replace")
        report = {"exit": status, "log": tail, "cases": [], "collected": 0}
        xmlfile = root / "results.xml"
        if phase == "test" and xmlfile.is_file() and xmlfile.stat().st_size <= 2_000_000:
            cases = ElementTree.parse(xmlfile).findall(".//testcase")
            report["collected"] = len(cases)
            for case in cases:
                name = case.attrib["name"].split("[", 1)[0]
                if name.startswith("test_ac_"):
                    report["cases"].append({
                        "module": case.attrib["classname"].split(".")[-1],
                        "name": name,
                        "passed": not any(child.tag in {"failure", "error", "skipped"}
                                          for child in case),
                    })
        return report


if __name__ == "__main__":
    print(json.dumps(execution(sys.argv[1], Path("/candidate"))))
