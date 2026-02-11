from .r_i18n import I18nConfigurator
from .log import LogConfigurator, LogMixin
import r_framework as r

import inspect
import typer
import typer.completion
import typer.core
from typer.core import TyperArgument
import click
from pathlib import Path
from i18n import t as _
from typing_extensions import override
from typing import Sequence, Annotated, Optional, Callable, Any
import typing


class App(LogMixin):
    def __init__(self, name: str, app_dir: Path):
        self.name = name
        self.app_dir = app_dir

    def boot(self, args: Sequence[str]):
        r.DEBUG = "--debug" in args

        self.configure_log(1 if r.DEBUG else 0)
        self.configure_i18n()

    def configure_log(self, verbosity: int):
        LogConfigurator().configure(verbosity)

    def configure_i18n(self):
        I18nConfigurator().configure(self.name, self.app_dir)


class TyperApp(App):
    class LazyHelp:
        """
        Lazy translation to allow flexible execution order.
        """

        pass

    Debug = Annotated[Optional[bool], typer.Option()]
    Verbose = Annotated[
        Optional[int],
        typer.Option(
            "-v",
            "--verbose",
            count=True,
            help="app.args.verbose",
        ),
        LazyHelp(),
    ]

    def register_command(self, func: Callable[..., Any]):
        self.typer.command(
            cls=self._TyperCommand,
            help=_(f"app.command.{func.__name__}"),
        )(func)

    @override
    def __init__(self, name: str, app_dir: Path):
        super().__init__(name, app_dir)

    @override
    def boot(self, args: Sequence[str]):
        super().boot(args)

        __, *metadata = typing.get_args(self.Verbose)
        metadata[0].callback = self._verbose_callback

        self.typer = typer.Typer(
            name=self.name,
            help=_("app.description"),
            options_metavar=_("click.options_metavar"),
            subcommand_metavar=_("click.subcommand_metavar"),
        )

    def run(self, *args: Any):
        return self.typer(args=args)

    def _verbose_callback(self, verbosity: int):
        min_limit = 1 if r.DEBUG else 0
        self.configure_log(max(verbosity, min_limit))

    @classmethod
    def _translate_typer_parameters(
        cls, func: Callable[..., Any], typer_params: Sequence[click.Parameter]
    ):
        # lazy translation
        signatures = inspect.signature(func)
        for name, param in signatures.parameters.items():
            cls._lazy_translate_for_a_param(name, param, typer_params)

        # translate Typer internal options
        for p in typer_params:
            if p.callback and typer.completion.__name__ == p.callback.__module__:
                help_key = f"typer.completion.{p.callback.__name__}"
                help_msg = _(help_key)
                if help_msg != help_key:
                    assert isinstance(p, (click.Option, TyperArgument))
                    p.help = help_msg

    @classmethod
    def _lazy_translate_for_a_param(
        cls,
        name: str,
        param: inspect.Parameter,
        typer_params: Sequence[click.Parameter],
    ):
        annotation = param.annotation
        if Annotated is not typing.get_origin(annotation):
            return
        __, *metadata = typing.get_args(annotation)
        for meta in metadata:
            if not isinstance(meta, cls.LazyHelp):
                continue
            for p in typer_params:
                if p.name != name:
                    continue
                assert isinstance(p, (click.Option, TyperArgument))
                p.help = _(p.help or f"app.args.{name}")

    # Python supports diamond inheritance, where the same base class appears more than once in the hierarchy.
    # Each child class instance contains only one instance of the base class.
    # In contrast to PHP, Python defines method resolution order (MRO) at the language level.
    class _TyperCommandMixin(click.Command):
        @override
        def format_help(self, ctx: click.Context, formatter: click.HelpFormatter):
            assert self.callback is not None
            TyperApp._translate_typer_parameters(self.callback, self.params)
            return super().format_help(ctx, formatter)

    class _TyperCommand(_TyperCommandMixin, typer.core.TyperCommand):
        pass

    class _TyperGroup(_TyperCommandMixin, typer.core.TyperCommand):
        pass
