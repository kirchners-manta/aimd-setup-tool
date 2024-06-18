"""
Script to build input files for CP2K simulations, based on pre-defined input snippets.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

from ..functions import getFileList, make_project_dir


def generate_input_files(data: dict[str, Any], joblist: list[bool]) -> None:
    """Generate input files for CP2K simulations.

    Parameters
    ----------
    data : dict[str, Any]
        Dictionary containing the input parameters specified by the user.
    joblist : list[bool]
        List of boolean values indicating if the input files should be generated.
        Entries correspond to the following jobs:
        - geometry optimization
        - equilibration
        - relaxation
        - production
        - bqb file calculation
        - single point energy calculation
    """

    # where are the snippets located?
    snip_dir = os.path.dirname(__file__)

    # geometry optimization
    if joblist[0]:
        # create an empty list to store the input file lines
        lines = []
        # add global settings to the input file
        with open(Path(snip_dir, "global", "header.inp"), "r", encoding="utf-8") as f:
            lines.extend(f.readlines())
        # insert keywords of the global settings after the opening line
        # find the line number of the opening line
        for i, line in enumerate(lines):
            if "&GLOBAL" in line:
                with open(
                    Path(snip_dir, "global", "keywords.inp"), "r", encoding="utf-8"
                ) as f:
                    lines.insert(i + 1, f.read())

        for line in lines:
            print(line)

    # equilibration
    if joblist[1]:
        """"""
    # relaxation
    if joblist[2]:
        """"""
    # production
    if joblist[3]:
        """"""
    # bqb file calculation
    if joblist[4]:
        """"""
    # single point energy calculation
    if joblist[5]:
        """"""
