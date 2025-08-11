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
    toml_options = (
        toml.load(cli_args.input) if cli_args.input is not None else {}
    )
    # forgive confusion of "-" and "_" in toml/command line
    toml_options = {k.replace("-", "_"): v for k, v in toml_options.items()}
    # merge toml options with command line options, make sure that toml options override command line options
    args.update(toml_options)

    # hand over arguments to setup function
    return setup_job(args)
