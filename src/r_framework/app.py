# coding: utf-8
from .r_i18n import I18nConfigurator
from .log import LogConfigurator
import r_framework as r

import inspect
import typer
import typer.core
import click
from pathlib import Path
from i18n import t as _
from typing import Annotated, Optional, Callable
import typing

class App:
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
    def __init__(default = ..., *param_decls: str):
        pass
    #     func.__dict__[cls._LAZY_HELP_ARGS] = kwargs
    #     return func

class TyperApp(App):
    def register_command(self, func: Callable, name: str):
        self.typer.command(
            cls=self._TyperCommand,
            name = name,
        )(func)

    def __init__(self, name, app_dir):
        super().__init__(name, app_dir)

    def boot(self, args):
        super().boot(args)
        self.typer = typer.Typer(
            name=self.name,
            options_metavar=_('click.options_metavar'),
            subcommand_metavar=_('click.subcommand_metavar'),
        )

    def run(self, *args):
        self.typer.callback(
            invoke_without_command=True,
            cls=self._TyperGroup,
        )(self._typer_app_callback)

        # avoid showing the Commands section when there is only one command
        if 1 == len(self.typer.registered_commands):
            self.typer.registered_commands[0].hidden = True

        self.typer(args=args)

    def _typer_app_callback(self,
            debug: Annotated[Optional[bool], typer.Option()] = False,
            verbose: Annotated[Optional[int], typer.Option('-v', '-verbose', count=True, help='app.args.verbose'), LazyHelp()] = 0):
        self.configure_log(verbose)

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
        def format_help(self, ctx, formatter):
            TyperApp._translate_typer_parameters(self.callback, self.params)
            return super().format_help(ctx, formatter)

    class _TyperGroup(typer.core.TyperGroup):
        def format_help(self, ctx, formatter):
            TyperApp._translate_typer_parameters(self.callback, self.params)
            return super().format_help(ctx, formatter)
