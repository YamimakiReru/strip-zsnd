# coding: utf-8

from controller import StripZsndController
from r_framework import TyperApp, LazyHelp

import typer
from pathlib import Path
import sys
from typing import Annotated, Optional

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

class StripZsndApp(TyperApp):
    def __init__(self, app_dir: Path):
        super().__init__('strip-zsnd', app_dir)

    def boot(self, args):
        super().boot(args)
        self.register_command(self._do_strip, 'strip')

    def _do_strip(self,
            input: Annotated[str, typer.Argument(help='app.args.input'), LazyHelp()],
            output: Annotated[Optional[str], typer.Argument(help='app.args.output'), LazyHelp()] = None,
            min_duration: Annotated[Optional[int], typer.Option(help='zsnd.args.min_duration'), LazyHelp()] = 10,
            threshold: Annotated[Optional[float], typer.Option(help='zsnd.args.threshold'), LazyHelp()] = -80.0,
            detect: Annotated[Optional[bool], typer.Option(help='zsnd.args.detect'), LazyHelp()] = False,
            verbose: TyperApp.Verbose = 0,
            debug: TyperApp.Debug = False):
        return StripZsndController().strip(input, output, min_duration, threshold, detect)
