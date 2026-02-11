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

    _DEFAULT_CMD_KEY = "_default_cmd"

    @classmethod
    def default_cmd(cls, func: Callable[..., Any]):
        """
        A decorator that marks a function as the default subcommand
        """
        func.__dict__[cls._DEFAULT_CMD_KEY] = True
        return func

    def register_command(self, func: Callable[..., Any]):
        self.typer.command(
            cls=self._TyperCommand,
            help=_(f"app.command.{func.__name__}"),
        )(func)

    def register_callback(self, func: Callable[..., Any]):
        self.typer.callback(
            cls=self._TyperGroup,
            invoke_without_command=True,
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
        if 2 <= len(self.typer.registered_commands):
            self.typer.callback(
                cls=self._TyperGroup,
                invoke_without_command=True,
            )(self._typer_callback)
        return self.typer(args=args)

    def _verbose_callback(self, verbosity: int):
        min_limit = 1 if r.DEBUG else 0
        self.configure_log(max(verbosity, min_limit))

    def _typer_callback(self, verbose: Verbose = 0, debug: Debug = False):
        """
        Only a stub used to hold command line options.
        """
        pass

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

    class _TyperGroup(_TyperCommandMixin, typer.core.TyperGroup):
        _default_cmd: str | None = None

        @override
        def parse_args(self, ctx: click.Context, args: list[str]):
            # check whether the user explicitly specified a subcommand
            cmd_pos = 0
            for cmd in args:
                if not cmd.startswith("-"):
                    break
                cmd_pos += 1
            is_cmd_found = len(args) > cmd_pos

            if (not is_cmd_found) or (args[cmd_pos] not in self.commands):
                # no subcommand was specified

                # check whether the user specifies a help option
                for h in ctx.help_option_names:
                    if h in args:
                        # force the application to show its own help and exit.
                        # Typer would otherwise show an 'invalid command' error or the help of a subcommand.
                        click.echo(ctx.get_help())
                        raise typer.Exit(0)
                # attempt to invoke the subcommand marked as the default
                for cmd2 in self.commands.values():
                    if TyperApp._DEFAULT_CMD_KEY in cmd2.callback.__dict__:
                        assert cmd2.name is not None
                        args.insert(cmd_pos if is_cmd_found else 0, cmd2.name)
            return super().parse_args(ctx, args)
