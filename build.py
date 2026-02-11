import shutil
import subprocess
from pathlib import Path
import os
import sys
from typing import Any

APP_NAME = "strip-zsnd"

SCRIPT_DIR = Path(__file__).resolve().parent


def run(cmd: tuple[str, ...], **kwargs: Any):
    subprocess.run(cmd, check=True, **kwargs)


def clean():
    for d in ["build", "dist"]:
        path = SCRIPT_DIR / d
        if path.exists():
            shutil.rmtree(path)


def main():
    os.chdir(SCRIPT_DIR)
    clean()

    # Get python.exe in venv
    venv_python = SCRIPT_DIR / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        print('venv not found. Run "python -m venv .venv" at first.')
        return 1

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SCRIPT_DIR / "src")

    # pyinstaller
    run(
        (
            str(venv_python),
            "-m",
            "PyInstaller",
            f"{APP_NAME}.spec",
        ),
        env=env,
    )

    shutil.copytree(
        SCRIPT_DIR / "locales", SCRIPT_DIR / "dist" / "locales", dirs_exist_ok=True
    )

    # test run
    run(
        (
            str(SCRIPT_DIR / "dist" / f"{APP_NAME}.exe"),
            "--debug",
            "--help",
        )
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
