import zipfile
import shutil
import subprocess
from pathlib import Path
import os
import sys
from typing import Any

APP_NAME = "strip-zsnd"
SCRIPT_DIR = Path(__file__).resolve().parent
DIST_DIR = SCRIPT_DIR / "dist"
DIST_APP_DIR = DIST_DIR / APP_NAME

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

    shutil.copytree(SCRIPT_DIR / "locales", DIST_APP_DIR / "locales", dirs_exist_ok=True)
 
    with zipfile.ZipFile(DIST_DIR / f"{APP_NAME}.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for file in DIST_APP_DIR.rglob("*"):
            if file.is_dir():
                continue
            z.write(file, file.relative_to(DIST_APP_DIR))

    # test run
    run(
        (
            str(DIST_APP_DIR / f"{APP_NAME}.exe"),
            "--debug",
            "--help",
        )
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
