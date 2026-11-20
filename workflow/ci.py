"""Trusted entry point for the independently dispatched CI check."""

import sys
from pathlib import Path

from common import dump, markdown
from sandbox import check


def main():
    repo, directory = map(lambda name: Path(name).resolve(), sys.argv[1:])
    directory.mkdir(parents=True, exist_ok=True)
    for phase in ("build", "test"):
        result = check(repo, phase)
        dump(directory / f"{phase}.json", result)
        if result["exit"] or (phase == "test" and not result["collected"]):
            markdown(directory / "ci.md", "CI", f"The {phase} check failed.")
            raise SystemExit(f"CI {phase} failed. See the CI artifact.")
    markdown(directory / "ci.md", "CI", "Wheel build and full pytest suite passed.")


if __name__ == "__main__":
    main()
