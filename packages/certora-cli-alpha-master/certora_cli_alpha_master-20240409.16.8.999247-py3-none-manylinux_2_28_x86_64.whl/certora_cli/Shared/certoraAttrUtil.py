import sys
import argparse
from typing import Any, NoReturn, Dict, Optional, Callable
from Shared import certoraUtils as Util
from enum import auto
from dataclasses import dataclass, field
from rich.console import Console
from rich.table import Table
from rich.text import Text

APPEND = 'append'
STORE_TRUE = 'store_true'
VERSION = 'version'
SINGLE_OR_NONE_OCCURRENCES = '?'
MULTIPLE_OCCURRENCES = '*'
ONE_OR_MORE_OCCURRENCES = '+'


def default_validation(x: Any) -> Any:
    return x


class UniqueStore(argparse.Action):
    """
    This class makes the argparser throw an error for a given flag if it was inserted more than once
    """

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Any,  # type: ignore
                 option_string: str) -> None:
        if getattr(namespace, self.dest, self.default) is not self.default:
            parser.error(f"{option_string} appears several times.")
        setattr(namespace, self.dest, values)


class NotAllowed(argparse.Action):
    """
    This class makes the argparser throw an error for a given flag if it was set in CLI (can be set using conf file)
    """

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Any,  # type: ignore
                 option_string: str) -> None:

        parser.error(f"{option_string} cannot be set in command line only in a conf file.")


class CertoraArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> NoReturn:
        prefix = 'unrecognized arguments: '
        is_single_dash_flag = False

        if message.startswith(prefix):
            flag = message[len(prefix):].split()[0]
            if len(flag) > 1 and flag[0] == '-' and flag[1] != '-':
                is_single_dash_flag = True
        self.print_help(sys.stderr)
        if is_single_dash_flag:
            Console().print(f"{Util.NEW_LINE}[bold red]Please remember, CLI flags should be preceded with "
                            f"double dashes!{Util.NEW_LINE}")
        raise Util.CertoraArgParseError(message)


class AttrArgType(Util.NoValEnum):
    STRING = auto()
    BOOLEAN = auto()
    LIST = auto()
    INT = auto()
    MAP = auto()


class BaseAttribute(Util.NoValEnum):
    def get_flag(self) -> str:
        return self.value.flag if self.value.flag is not None else '--' + str(self)

    @classmethod
    def print_attr_help(cls) -> None:

        table = Table(padding=(1, 1), show_lines=True, header_style="bold orange4")

        table.add_column(Text("Flag", justify="center"), style="cyan", no_wrap=True, width=40)
        table.add_column(Text("Description", justify="center"), style="magenta", width=80)
        table.add_column(Text("Type", justify="center"), style="magenta", justify='center', width=30)

        for attr in cls:
            if attr.value.help_msg != '==SUPPRESS==' and attr.get_flag().startswith('--') \
               and not attr.value.deprecation_msg:
                table.add_row(attr.get_flag(), attr.value.help_msg, str(attr.value.arg_type))
        console = Console()
        console.print(table)


@dataclass
class BaseArgument:
    flag: Optional[str] = None  # override the 'default': option name
    attr_validation_func: Callable = default_validation
    help_msg: str = argparse.SUPPRESS
    # args for argparse's add_attribute passed as is
    argparse_args: Dict[str, Any] = field(default_factory=dict)
    arg_type: AttrArgType = AttrArgType.STRING
    deprecation_msg: Optional[str] = None
