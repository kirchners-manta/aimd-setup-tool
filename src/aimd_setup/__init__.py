"""
AIMD Setup Tool
===============

This tool is used to setup AIMD calculations for CP2K.
It is mainly designed for AIMD simulations and the subsequent calculation vibrational spectra.
Further functionality is planned.
The program creates a project directory, copies the input files, adjusts them to the given parameters,
and creates a runscript to submit the calculation to the cluster.
This program is developed by Tom Frömbgen, (Group of Prof. Dr. Barbara Kirchner, University of Bonn, Germany) and maily designed for the use in this group.
It is published under the MIT license.
"""

from .__version__ import __version__
from .cli import console_entry_point