import webbrowser
import subprocess
from pathlib import Path
import os
import sys
from typing import Any


def run(cmd: tuple[str, ...], **kwargs: Any):
    subprocess.run(cmd, check=True, **kwargs)


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)

    # Get python.exe in venv
    venv_python = script_dir / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        print('venv not found. Run "python -m venv .venv" at first.')
        return 1

    report_name = "test-report"

    # pytest
    run(
        (
            str(venv_python),
            "-m",
            "pytest",
            f"--html={report_name}.html",
            "--self-contained-html",
            f"--css={report_name}.css",
        )
    )

    # Open HTML
    webbrowser.open(f"{report_name}.html")

    return 0


if __name__ == "__main__":
    sys.exit(main())
