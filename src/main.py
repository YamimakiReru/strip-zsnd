from web_controller import WebStripZsndController
from cli_controller import StripZsndController
from r_framework import TyperApp
LazyHelp = TyperApp.LazyHelp
import r_framework as r

import typer
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
        self.register_command(self.strip)
        self.register_command(self.webui)

    def strip(self,
            input_path: Annotated[Path, typer.Argument(
                dir_okay=False,
                exists=True,
                readable=True,
                ), LazyHelp()],
            output_path: Annotated[Optional[Path], typer.Argument(
                dir_okay=False,
                writable=True,
                ), LazyHelp()] = None,
            min_duration: Annotated[Optional[int], typer.Option(
                '-d', '--duration',
                min=0,
                ), LazyHelp()] = 10,
            threshold: Annotated[Optional[float], typer.Option(
                '-t', '--threshold',
                max=-10.0,
                ), LazyHelp()] = -80.0,
            detect_only: Annotated[Optional[bool], typer.Option(
                '--detect',
                ), LazyHelp()] = False,
            force: Annotated[Optional[bool], typer.Option(
                '-f/-i', '--force',
            ), LazyHelp()] = False,
            verbose: TyperApp.Verbose = 0,
            debug: TyperApp.Debug = False,
            ctx: typer.Context = typer.Option(None)):
        if r.DEBUG or verbose:
            self.get_logger().debug(ctx.params)

        output_path_str = None if output_path is None else str(output_path)
        return StripZsndController().strip(str(input_path), output_path_str, force,
                min_duration, threshold, detect_only)

    def webui(self, port: Annotated[Optional[int], typer.Option(
            '-p', '--port',
            min= 1024,
            max=49151,
    ), LazyHelp()] = 14514):
        return WebStripZsndController.serve(port)
