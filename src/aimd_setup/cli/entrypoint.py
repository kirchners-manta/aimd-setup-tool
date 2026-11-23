"""
Entrypoint for command line interface.
"""

from __future__ import annotations

import sys
import tomllib
from collections.abc import Sequence

from ..argparser import parser
from ..setup import setup_job

# TOML keys of renamed options; unknown keys would otherwise be ignored silently
RENAMED_OPTIONS = {"n_bqb": "n_chunks", "steps_bqb": "steps_chunk"}


def console_entry_point(argv: Sequence[str] | None = None) -> int:
    """Parse the command line and an optional TOML file, then set up the job.

    Parameters
    ----------
    argv : Sequence[str] | None, optional
        Command line arguments without the program name. If None, the
        arguments are read from ``sys.argv``.

    Returns
    -------
    int
        Exit code.

    Raises
    ------
    SystemExit
        If the TOML file uses the old name of a renamed option.
    """

    # get arguments from command line and parse them, form dictionary
    cli_args = parser().parse_args(argv)
    args = vars(cli_args)
    # load toml options
    toml_options = {}
    if cli_args.input is not None:
        with open(cli_args.input, "rb") as f:
            toml_options = tomllib.load(f)
    # forgive confusion of "-" and "_" in toml/command line
    toml_options = {k.replace("-", "_"): v for k, v in toml_options.items()}
    for old, new in RENAMED_OPTIONS.items():
        if old in toml_options:
            sys.exit(
                f" *** Option '{old}' was renamed to '{new}'. Update the TOML file. Exiting."
            )
    # merge toml options with command line options, make sure that toml options override command line options
    args.update(toml_options)

    # hand over arguments to setup function
    return setup_job(args)
