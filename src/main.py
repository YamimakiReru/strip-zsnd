# coding: utf-8

from strip_zsnd import StripZsndApp
from pathlib import Path
import sys

def main():
    app_dir = ''
    if getattr(sys, 'frozen', False):
        # executed inside a PyInstaller frozen app
        app_dir = Path(sys.executable).resolve().parent
    else:
        app_dir = Path(__file__).resolve().parents[1]

    the_app = StripZsndApp(app_dir)
    the_app.boot(sys.argv)
    the_app.run(*sys.argv[1:])
