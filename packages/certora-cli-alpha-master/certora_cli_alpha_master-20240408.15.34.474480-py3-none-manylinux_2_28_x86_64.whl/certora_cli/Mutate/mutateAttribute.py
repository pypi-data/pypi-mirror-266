import sys
import argparse
from dataclasses import dataclass
from enum import unique
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.text import Text


scripts_dir_path = Path(__file__).parent.resolve()  # containing directory
sys.path.insert(0, str(scripts_dir_path))

from Shared import certoraValidateFuncs as Vf
from Shared import certoraUtils as Util
from Shared import certoraAttrUtil as AttrUtil
from Mutate import mutateConstants as Constants


MUTATION_DOCUMENTATION_URL = 'https://docs.certora.com/en/latest/docs/gambit/mutation-verifier.html#cli-options'

@dataclass
class MutateArgument(AttrUtil.BaseArgument):
    pass

@unique
class MutateAttribute(AttrUtil.BaseAttribute):

    # this flag is for handling getting a conf file using positional arg (i.e. without --<flag>).
    # so both "cerotraMutate xxx.conf" and "certoraMutate --conf xxx.conf" are legal.
    # During validation, we will verify that only one conf file was defined.
    CONF_NO_FLAG = MutateArgument(
        flag='conf_no_flag',
        argparse_args={
            'type': Path,
            'nargs': '?',
            'action': AttrUtil.UniqueStore
        }
    )

    CONF = MutateArgument(
        help_msg="Settings for both the prover and the mutation engine",
        attr_validation_func=Vf.validate_json5_file,
        argparse_args={
            'type': Path,
            'action': AttrUtil.UniqueStore
        }
    )

    ORIG_RUN = MutateArgument(
        help_msg="A link to a previous run of the Prover on the original program, will be used as the basis for the "
                 "generated mutations",
        attr_validation_func=Vf.validate_orig_run,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    MSG = MutateArgument(
        help_msg="Message to annotate the current certoraMutate run.",
        attr_validation_func=Vf.validate_msg,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    SERVER = MutateArgument(
        attr_validation_func=Vf.validate_server_value,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    PROVER_VERSION = MutateArgument(
        attr_validation_func=Vf.validate_prover_version,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    DEBUG = MutateArgument(
        flag='--debug',    # added to prevent dup with DUMP_CSV
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    ORIG_RUN_DIR = MutateArgument(
        help_msg="The folder where the files will be downloaded from the original run link.",
        # attr_validation_func=Vf.validate_writable_path,
        argparse_args={
            'type': Path,
            'action': AttrUtil.UniqueStore
        }
    )

    OUTDIR = MutateArgument(
        help_msg=f"Specifies the output directory for all gambit runs (defaults to '{Constants.GAMBIT_OUT}')",
        # attr_validation_func=Vf.validate_writable_path,
        argparse_args={
            'type': Path,
            'action': AttrUtil.UniqueStore
        }
    )

    GAMBIT_ONLY = MutateArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="Stops processing after generating mutations with Gambit.",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    DUMP_FAILED_COLLECTS = MutateArgument(
        # attr_validation_func=Vf.validate_writable_path,
        help_msg="Path to the log file capturing mutant collection failures.",
        argparse_args={
            'type': Path,
            'action': AttrUtil.UniqueStore
        }
    )

    # Sets a file that will store the object sent to mutation testing UI (useful for testing)
    UI_OUT = MutateArgument(
        argparse_args={
            'type': Path,
            'action': AttrUtil.UniqueStore
        }
    )

    DUMP_LINK = MutateArgument(
        flag='--dump_link',    # added to prevent dup with DUMP_CSV
        # todo - validation can write the file
        argparse_args={
            'type': Path,
            'action': AttrUtil.UniqueStore
        }
    )

    DUMP_CSV = MutateArgument(
        attr_validation_func=Vf.validate_writable_path,
        argparse_args={
            'type': Path,
            'action': AttrUtil.UniqueStore
        }
    )

    # Synchronous mode
    # Run the tool synchronously in shell
    SYNC = MutateArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    '''
    The file containing the links holding certoraRun report outputs.
    In async mode, run this tool with only this option.
    '''
    COLLECT_FILE = MutateArgument(
        flag='--collect_file',    # added to prevent dup with DUMP_CSV
        # attr_validation_func=Vf.validate_readable_file,
        argparse_args={
            'type': Path,
            'action': AttrUtil.UniqueStore
        }
    )

    '''
   The max number of minutes to poll after submission was completed,
    and before giving up on synchronously getting mutation testing results
   '''
    POLL_TIMEOUT = MutateArgument(
        flag='--poll_timeout',    # added to prevent dup with REQUEST_TIMEOUT
        attr_validation_func=Vf.validate_positive_integer,
        arg_type=AttrUtil.AttrArgType.INT,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    # The maximum number of retries a web request is attempted
    MAX_TIMEOUT_ATTEMPTS_COUNT = MutateArgument(
        arg_type=AttrUtil.AttrArgType.INT,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    # The timeout in seconds for a web request
    REQUEST_TIMEOUT = MutateArgument(
        attr_validation_func=Vf.validate_positive_integer,
        arg_type=AttrUtil.AttrArgType.INT,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    GAMBIT = MutateArgument(
        arg_type=AttrUtil.AttrArgType.MAP,
        argparse_args={
            'nargs': '*',
            'action': AttrUtil.NotAllowed
        }
    )
    # todo vvvv - parse_manual_mutations, change warnings to exceptions
    MANUAL_MUTANTS = MutateArgument(
        arg_type=AttrUtil.AttrArgType.MAP,
        attr_validation_func=Vf.validate_manual_mutants,
        flag='--manual_mutants',  # added to prevent dup with GAMBIT
        argparse_args={
            'nargs': '*',
            'action': AttrUtil.NotAllowed
        }
    )

    '''
    Add this if you wish to wait for the results of the original verification.
    Reasons to use it:
    - Saves resources - all the mutations will be ignored if the original fails
    - The Prover will use the solver data from the original run to reduce the run time of the mutants
    Reasons to not use it:
    - Run time will be increased
    '''
    #
    WAIT_FOR_ORIGINAL_RUN = MutateArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        flag='--wait_for_original_run',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    TEST = MutateArgument(
        attr_validation_func=Vf.validate_test_value,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    #  TODO - Move to base (rahav)
    def validate_value(self, value: str) -> None:
        if self.value.attr_validation_func is not None:
            try:
                self.value.attr_validation_func(value)
            except Util.CertoraUserInputError as e:
                msg = f'{self.get_flag()}: {e}'
                if isinstance(value, str) and value.strip()[0] == '-':
                    flag_error = f'{value}: Please remember, CLI flags should be preceded with double dashes. ' \
                                 f'{Util.NEW_LINE}For more help run the tool with the option --help'
                    msg = flag_error + msg
                raise Util.CertoraUserInputError(msg) from None


def get_args(args_list: List[str]) -> Dict:

    def formatter(prog: Any) -> argparse.HelpFormatter:
        return argparse.HelpFormatter(prog, max_help_position=100, width=200)

    parser = MutationParser(prog="certora-cli arguments and options", allow_abbrev=False,
                            formatter_class=formatter,
                            epilog="  -*-*-*   You can find detailed documentation of the supported options in "
                                   f"{MUTATION_DOCUMENTATION_URL}   -*-*-*")
    args = list(MutateAttribute)

    for arg in args:
        flag = arg.get_flag()
        if arg.value.arg_type == AttrUtil.AttrArgType.INT:
            parser.add_argument(flag, help=arg.value.help_msg, type=int, **arg.value.argparse_args)
        else:
            parser.add_argument(flag, help=arg.value.help_msg, **arg.value.argparse_args)
    return vars(parser.parse_args(args_list))


def print_attr_help() -> None:

    table = Table(title="CertoraMutate Flags", padding=(1, 1), show_lines=True, header_style="bold orange4")

    table.add_column(Text("Flag", justify="center"), style="cyan", no_wrap=True, width=40)
    table.add_column(Text("Description", justify="center"), style="magenta", width=80)
    table.add_column(Text("Type", justify="center"), style="magenta", justify='center', width=30)

    for attr in MutateAttribute:
        if attr.value.help_msg != '==SUPPRESS==' and attr.get_flag().startswith('--'):
            table.add_row(attr.get_flag(), attr.value.help_msg, str(attr.value.arg_type))

    console = Console()
    console.print(table)


class MutationParser(AttrUtil.CertoraArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def format_help(self) -> str:
        console = Console()
        console.print("\n\nThe Certora Mutate - A tool for generating and verifying mutations.")
        console.print("\n\n[bold orange4]Usage: certoraMutate <Flags>\n\n")

        console.print("Flag Types\n", style="bold underline orange4")

        console.print("[cyan]boolean:[/cyan] gets no value, sets flag value to true (false is always the default)",
                      style="orange4")
        console.print("[cyan]string:[/cyan] gets a single string as a value, note also numbers are of type string\n\n",
                      style="orange4")

        print_attr_help()
        console.print("\n\n[bold orange4]You can find detailed documentation of the supported flags[/] "
                      f"[link={MUTATION_DOCUMENTATION_URL}]here[/link]\n\n")

        return ''
