# coding: utf-8

from pathlib import Path
import sys

if not getattr(sys, 'frozen', False):
    # NOT executed inside a PyInstaller frozen app
    # -> inserts src_dir after current directory
    script_dir = Path(__file__).resolve().parent
    src_dir = str(script_dir / 'src')
    sys.path.insert(min(1, len(sys.path)), src_dir)

from main import main

if '__main__' == __name__:
    main()
