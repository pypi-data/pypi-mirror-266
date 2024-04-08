#!/usr/bin/env python3

import sys

from pathlib import Path
from typing import List
from types import SimpleNamespace
import logging
from rich.console import Console


scripts_dir_path = Path(__file__).parent.resolve()  # containing directory
sys.path.insert(0, str(scripts_dir_path))

from Shared.certoraLogging import LoggingManager
from Shared import certoraUtils as Util

from Mutate import mutateApp as App
from Mutate import mutateValidate as Mv
from Mutate import mutateConstants as Constants

mutate_logger = logging.getLogger("mutate")

def mutate_entry_point() -> None:
    run_mutate(sys.argv[1:])


# signature same as run_certora -> second args only for polymorphism

def run_mutate(sys_args: List[str], _: bool = False) -> None:
    try:
        logging_manager = LoggingManager()
        if '--debug' in sys_args:
            logging_manager.set_log_level_and_format(debug=True)

        mutate_app = App.MutateApp()
        mutate_app.get_args(sys_args)
        mutate_app.set_conf_file()

        if mutate_app.conf:
            run_mutate_generate(mutate_app)
        else:
            run_mutate_collect(mutate_app)

    except Util.CertoraArgParseError as e:
        Console().print(f"[bold red]{e}")
        sys.exit(1)
    except KeyboardInterrupt:
        Console().print("[bold red]\nInterrupted by user")
        sys.exit(1)


def run_mutate_collect(mutate_app: App.MutateApp) -> None:
    if not mutate_app.collect_file:
        mutate_app.collect_file = Constants.DEFAULT_COLLECT_FILE
    ready = mutate_app.collect()
    if not ready:
        raise Util.CertoraUserInputError("The report might broken because some "
                                         "results could not be fetched. "
                                         f"Check the {mutate_app.collect_file} file to investigate.")


def run_mutate_generate(mutate_app: App.MutateApp) -> None:

    mutate_app.read_conf_file()
    mutate_app.checks_before_settings_defaults()
    mutate_app.set_defaults()

    if mutate_app.orig_run:
        mutate_app.read_conf_from_orig_run()

    mutate_app.settings_post_parsing()
    Util.check_packages_arguments(SimpleNamespace(**mutate_app.prover_dict))

    validator = Mv.MutateValidator(mutate_app)
    validator.validate()

    if mutate_app.test == str(Util.TestValue.CHECK_ARGS):
        raise Util.TestResultsReady(mutate_app)

    # default mode is async. That is, we both _submit_ and _collect_
    if mutate_app.sync:
        App.check_key_exists()
        # sync mode means we submit, then we poll for the specified amount of minutes

        mutate_app.submit()
        mutate_app.poll_collect()
    else:
        App.check_key_exists()
        mutate_app.submit()


if __name__ == '__main__':
    mutate_entry_point()
