"""
Entrypoint for command line interface.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..argparser import parser
from ..setup import setup_job


def console_entry_point(argv: Sequence[str] | None = None) -> int:

    # get arguments from command line and parse them
    args = parser().parse_args(argv)

    # hand over arguments to setup function
    setup_job(args)

    return 0
