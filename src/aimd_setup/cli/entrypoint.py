"""
Entrypoint for command line interface.
"""

from __future__ import annotations

from collections.abc import Sequence

import toml  # type: ignore

from ..argparser import parser
from ..setup import setup_job


def console_entry_point(argv: Sequence[str] | None = None) -> int:

    # get arguments from command line and parse them, form dictionary
    cli_args = parser().parse_args(argv)
    args = vars(cli_args)
    # load toml options
    toml_options = toml.load(cli_args.input) if cli_args.input is not None else {}
    # merge toml options with command line options
    args.update(toml_options)

    # hand over arguments to setup function
    setup_job(args)

    return 0
