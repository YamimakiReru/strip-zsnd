from controller import StripZsndController
from r_framework import TyperApp, LazyHelp

import typer
import click
from pathlib import Path
import sys
from typing_extensions import override
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

    @override
    def boot(self, args):
        super().boot(args)
        self.register_command(self._do_strip, 'strip')

    def _do_strip(self,
            input: Annotated[Path, typer.Argument(
                help='app.args.input',
                click_type=click.Path(dir_okay=False, exists=True, readable=True),
                ),LazyHelp()],
            output: Annotated[Optional[Path], typer.Argument(
                help='app.args.output',
                click_type=click.Path(dir_okay=False, writable=True),
                ), LazyHelp()] = None,
            min_duration: Annotated[Optional[int], typer.Option(
                '-d', '--duration',
                help='zsnd.args.min_duration',
                click_type=click.IntRange(min=0, min_open=True),
                ), LazyHelp()] = 10,
            threshold: Annotated[Optional[float], typer.Option(
                '-t', '--threshold',
                help='zsnd.args.threshold',
                click_type=click.FloatRange(max=-10.0)
                ), LazyHelp()] = -80.0,
            detect_only: Annotated[Optional[bool], typer.Option(
                '--detect',
                help='zsnd.args.detect',
                ), LazyHelp()] = False,
            force: Annotated[Optional[bool], typer.Option(
                '-f/-i', '--force',
                help='app.args.force',
            ), LazyHelp()] = False,
            verbose: TyperApp.Verbose = 0,
            debug: TyperApp.Debug = False):
        return StripZsndController().strip(str(input), str(output), force,
                min_duration, threshold, detect_only)
