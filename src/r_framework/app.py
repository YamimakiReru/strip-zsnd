from .r_i18n import I18nConfigurator
from .log import LogConfigurator, LogMixin
import r_framework as r

import inspect
import typer
import typer.core
import click
from pathlib import Path
from i18n import t as _
from typing_extensions import override
from typing import Annotated, Optional, Callable
import typing

class App(LogMixin):
    def __init__(self, name: str, app_dir: Path):
        self.name = name
        self.app_dir = app_dir

    def boot(self, args: list[str]):
        r.DEBUG = '--debug' in args

        self.configure_log(1 if r.DEBUG else 0)
        self.configure_i18n()

    def configure_log(self, verbosity: int):
        LogConfigurator().configure(verbosity)

    def configure_i18n(self):
        I18nConfigurator().configure(self.name, self.app_dir)

class LazyHelp:
    '''
    Lazy translation to allow flexible execution order.
    '''
    pass

class TyperApp(App):
    Debug = Annotated[Optional[bool], typer.Option()]
    Verbose = Annotated[Optional[int], typer.Option(
        '-v', '--verbose',
        count=True,
        help='app.args.verbose',
    ), LazyHelp()]

    def register_command(self, func: Callable, name: str):
        self.typer.command(
            cls=self._TyperCommand,
            name = name,
            help=_('app.description'),
        )(func)

    @override
    def __init__(self, name, app_dir):
        super().__init__(name, app_dir)

    @override
    def boot(self, args):
        super().boot(args)

        base_type, *metadata = typing.get_args(self.Verbose)
        metadata[0].callback = self._verbose_callback

        self.typer = typer.Typer(
            name=self.name,
            help=_('app.description'),
            options_metavar=_('click.options_metavar'),
            subcommand_metavar=_('click.subcommand_metavar'),
        )

    def run(self, *args):
        self.typer(args=args)

    def _verbose_callback(self, verbosity):
        min_limit = 1 if r.DEBUG else 0
        self.configure_log(max(verbosity, min_limit))

    @classmethod
    def _translate_typer_parameters(cls, func: Callable, typer_params: list[click.Option|click.Argument]):
        # lazy translation
        signatures = inspect.signature(func)
        for name, param in signatures.parameters.items():
            cls._lazy_translate_for_a_param(name, param, typer_params)

        # translate Typer internal options
        for p in typer_params:
            if p.callback and \
                    typer.completion.__name__ == p.callback.__module__:
                help_key = f'typer.completion.{p.callback.__name__}'
                help_msg = _(help_key)
                if help_msg != help_key:
                    p.help = help_msg

    @classmethod
    def _lazy_translate_for_a_param(cls, name: str, param: inspect.Parameter, typer_params: list[click.Option|click.Argument]):
        annotation = param.annotation
        if Annotated is not typing.get_origin(annotation):
            return
        base_type, *metadata = typing.get_args(annotation)
        for meta in metadata:
            if not isinstance(meta, LazyHelp):
                continue
            for p in typer_params:
                if p.name != name:
                    continue
                p.help = _(p.help)

    class _TyperCommand(typer.core.TyperCommand):
        @override
        def format_help(self, ctx, formatter):
            TyperApp._translate_typer_parameters(self.callback, self.params)
            return super().format_help(ctx, formatter)

    class _TyperGroup(typer.core.TyperGroup):
        @override
        def format_help(self, ctx, formatter):
            TyperApp._translate_typer_parameters(self.callback, self.params)
            return super().format_help(ctx, formatter)
