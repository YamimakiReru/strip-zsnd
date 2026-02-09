import subprocess
from pathlib import Path
import os
import sys

def run(cmd, **kwargs):
    subprocess.run(cmd, check=True, **kwargs)

def main() -> int:
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)

    # Get python.exe in venv
    venv_python = script_dir / '.venv' / 'Scripts' / 'python.exe'
    if not venv_python.exists():
        print('venv not found. Run "python -m venv .venv" at first.')
        return 1

    report_name = 'test-report'

    # pytest
    run([
        str(venv_python),
        '-m', 'pytest',
        f'--html={report_name}.html',
        '--self-contained-html',
        f'--css={report_name}.css',
    ])

    # Open HTML
    # TODO: Replace with webbrowser.open()
    run(['start', f'{report_name}.html'], shell=True)

    return 0

if __name__ == '__main__':
    sys.exit(main())
