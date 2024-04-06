import sys
import argparse
from typing import Any, NoReturn, Dict, Optional, Callable
from Shared import certoraUtils as Util
from enum import auto
from dataclasses import dataclass, field
from rich.console import Console


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


@dataclass
class BaseArgument:
    flag: Optional[str] = None  # override the 'default': option name
    attr_validation_func: Callable = default_validation
    help_msg: str = argparse.SUPPRESS
    # args for argparse's add_attribute passed as is
    argparse_args: Dict[str, Any] = field(default_factory=dict)
    arg_type: AttrArgType = AttrArgType.STRING
