# Part of the AIMD setup tool

"""
Parser for command line options.
"""

#############################################

from __future__ import annotations

import argparse
from pathlib import Path

from .. import __version__

# define constants
ELEMENTS = [
    "H",
    "He",
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Ne",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
    "K",
    "Ca",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Br",
    "Kr",
    "Rb",
    "Sr",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Tc",
    "Ru",
    "Rh",
    "Pd",
    "Ag",
    "Cd",
    "In",
    "Sn",
    "Sb",
    "Te",
    "I",
    "Xe",
    "Cs",
    "Ba",
    "La",
    "Ce",
    "Pr",
    "Nd",
    "Pm",
    "Sm",
    "Eu",
    "Gd",
    "Tb",
    "Dy",
    "Ho",
    "Er",
    "Tm",
    "Yb",
    "Lu",
    "Hf",
    "Ta",
    "W",
    "Re",
    "Os",
    "Ir",
    "Pt",
    "Au",
    "Hg",
    "Tl",
    "Pb",
    "Bi",
    "Po",
    "At",
    "Rn",
    "Fr",
    "Ra",
    "Ac",
    "Th",
    "Pa",
    "U",
    "Np",
    "Pu",
    "Am",
    "Cm",
    "Bk",
    "Cf",
    "Es",
    "Fm",
    "Md",
    "No",
    "Lr",
    "Rf",
    "Db",
    "Sg",
    "Bh",
    "Hs",
    "Mt",
    "Ds",
    "Rg",
    "Cn",
    "Nh",
    "Fl",
    "Mc",
    "Lv",
    "Ts",
    "Og",
]
EXTRA_ATOM_TYPES = ["D"]


# file and directory checks
def is_file(path: str | Path) -> str | Path:
    p = Path(path)

    if p.is_dir():
        raise argparse.ArgumentTypeError(
            f"Cannot open '{path}': Is a directory.",
        )

    if p.is_file() is False:
        raise argparse.ArgumentTypeError(
            f"Cannot open '{path}': No such file.",
        )

    return path


def is_dir(path: str | Path) -> str | Path:
    p = Path(path)

    if p.is_file():
        raise argparse.ArgumentTypeError(
            f"Cannot open '{path}': Is not a directory.",
        )

    if p.is_dir() is False:
        raise argparse.ArgumentTypeError(
            f"Cannot open '{path}': No such file or directory.",
        )

    return path


# custom actions
def action_not_less_than(min_value: float = 0.0) -> type[argparse.Action]:
    class CustomActionLessThan(argparse.Action):
        """
        Custom action for limiting possible input values. Raise error if value is smaller than min_value.
        """

        def __call__(
            self,
            p: argparse.ArgumentParser,
            args: argparse.Namespace,
            values: list[float | int] | float | int,  # type: ignore
            option_string: str | None = None,
        ) -> None:

            if isinstance(values, (int, float)):
                values = [values]

            if any(value < min_value for value in values):
                p.error(
                    f"Option '{option_string}' takes only values larger than {min_value}. {values} is not accepted."
                )

            if len(values) == 1:
                values = values[0]

            setattr(args, self.dest, values)

    return CustomActionLessThan


def action_not_more_than(max_value: float = 0.0) -> type[argparse.Action]:
    class CustomActionMoreThan(argparse.Action):
        """
        Custom action for limiting possible input values. Raise error if value is larger than max_value.
        """

        def __call__(
            self,
            p: argparse.ArgumentParser,
            args: argparse.Namespace,
            values: list[float | int] | float | int,  # type: ignore
            option_string: str | None = None,
        ) -> None:
            if isinstance(values, (int, float)):
                values = [values]

            if any(value > max_value for value in values):
                p.error(
                    f"Option '{option_string}' takes only values smaller than {max_value}. {values} is not accepted."
                )

            if len(values) == 1:
                values = values[0]

            setattr(args, self.dest, values)

    return CustomActionMoreThan


def action_in_range(
    min_value: float = 0.0, max_value: float = 1.0
) -> type[argparse.Action]:
    class CustomActionInRange(argparse.Action):
        """
        Custom action for limiting possible input values in a range. Raise error if value is not in range [min_value, max_value].
        """

        def __call__(
            self,
            p: argparse.ArgumentParser,
            args: argparse.Namespace,
            values: list[float | int] | float | int,  # type: ignore
            option_string: str | None = None,
        ) -> None:
            if isinstance(values, (int, float)):
                values = [values]

            if any(value < min_value or value > max_value for value in values):
                p.error(
                    f"Option '{option_string}' takes only values between {min_value} and {max_value}. {values} is not accepted."
                )

            if len(values) == 1:
                values = values[0]

            setattr(args, self.dest, values)

    return CustomActionInRange


def action_check_dftu() -> type[argparse.Action]:
    class CustomActionDFTU(argparse.Action):
        """
        Custom action for DFT+U. Check if the correct number of arguments is given.
        """

        def __call__(
            self,
            p: argparse.ArgumentParser,
            args: argparse.Namespace,
            values: list[str | float | int],  # type: ignore
            option_string: str | None = None,
        ) -> None:
            # check if number of arguments is correct
            if len(values) % 3 != 0:
                p.error(
                    f"Option '{option_string}' takes three arguments per atom type: Atom type, orbital angular momentum quantum number, U-J value in eV."
                )
            # iterate over each group of three arguments
            for i in range(0, len(values), 3):
                # check if atom type is valid
                if values[i] not in ELEMENTS + EXTRA_ATOM_TYPES:
                    p.error(
                        f"Option '{option_string}' takes only valid elements / atom types. {values[i]} is not accepted."
                    )
                # check if orbital angular momentum quantum number is valid
                if values[i + 1] not in ["0", "1", "2", "3"]:
                    p.error(
                        f"Option '{option_string}' takes only orbital angular momentum quantum numbers 0, 1, 2, 3. {values[i+1]} is not accepted."
                    )
                # check if U-J value is a physical
                if float(values[i + 2]) < 0:
                    p.error(
                        f"Option '{option_string}' takes only positive values for U-J. {values[i+2]} is not accepted."
                    )

            setattr(args, self.dest, values)

    return CustomActionDFTU


# custom formatter
class Formatter(argparse.HelpFormatter):
    """
    Custom format for help message.
    """

    def _get_help_string(self, action: argparse.Action) -> str | None:
        """
        Append default value and type of action to help string.

        Parameters
        ----------
        action : argparse.Action
            Command line option.

        Returns
        -------
        str | None
            Help string.
        """
        helper = action.help
        if helper is not None and "%(default)" not in helper:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]

                if action.option_strings or action.nargs in defaulting_nargs:
                    helper += "\n - default: %(default)s"
                # uncomment if type is needed to be shown in help message
                # if action.type:
                #     helper += "\n - type: %(type)s"

        return helper

    def _split_lines(self, text: str, width: int) -> list[str]:
        """
        Re-implementation of `RawTextHelpFormatter._split_lines` that includes
        line breaks for strings starting with 'R|'.

        Parameters
        ----------
        text : str
            Help message.
        width : int
            Text width.

        Returns
        -------
        list[str]
            Split text.
        """
        if text.startswith("R|"):
            return text[2:].splitlines()

        # pylint: disable=protected-access
        return argparse.HelpFormatter._split_lines(self, text, width)


# custom parser
def parser(name: str = "aimd-setup") -> argparse.ArgumentParser:
    """
    Parses the command line arguments.

    Returns
    -------
    argparse.ArgumentParser
        Container for command line arguments.
    """

    p = argparse.ArgumentParser(
        prog=name,
        description="Script to setup AIMD simulations or BQB file productions with CP2K.",
        epilog="Written for the Kirchner group by Tom Frömbgen. Internal use only.",
        formatter_class=lambda prog: Formatter(prog, max_help_position=60),
        add_help=False,
    )
    p.add_argument(
        "-p",
        "--project",
        type=str,
        help="R|Name of the project. Has to be given via command line or input file.\nA directory with this name will be created.",
        default=None,
        dest="project",
    )
    p.add_argument(
        "-c",
        "--coord",
        type=is_file,
        help="R|Coordinate file (in xyz format). Has to be given via command line or input file.",
        dest="coord",
        metavar="FILE",
        default=None,
    )
    p.add_argument(
        "-b",
        "--boxsize",
        type=float,
        dest="boxsize",
        help="R|Box edge length in Angstrom. Has to be given via command line, input file or in the second line of the coordinate file.\nFor cubic boxes only one value is needed.\nFor non-cubic boxes, supply a, b, c (space separated).",
        metavar="LENGTH",
        default=None,
        nargs="+",
        action=action_not_less_than(5.0),
    )
    p.add_argument(
        "-i",
        "--input",
        type=is_file,
        help="R|Input file containing the CP2K settings to be used by this script.",
        dest="input",
        metavar="FILE",
        default=None,
    )
    p.add_argument(
        "--basis",
        type=str,
        help="R|Basis set.",
        default="DZVP",
        dest="basis",
        choices=["svz", "dzvp", "tzvp", "tzv2p", "tzv2px"],
    )
    p.add_argument(
        "--bqb",
        help="R|Write BQB file during production run (can produce large file).\nDefault for type 'bqb'.",
        dest="bqb",
        action="store_true",
        default=False,
    )
    p.add_argument(
        "--chrg",
        type=int,
        metavar="N",
        help="R|Charge of the system.",
        default=0,
        dest="charge",
        action=action_in_range(-10, 10),
    )
    p.add_argument(
        "--cp2k-version",
        type=str,
        help="R|Version of CP2K to use.",
        default="2023.1",
        dest="cp2k_version",
        choices=["2023.1", "2025.1"],
    )
    p.add_argument(
        "--cpu",
        type=int,
        metavar="N",
        help="R|Number of CPUs to use.",
        default=64,
        dest="cpu",
        action=action_not_less_than(1),
    )
    p.add_argument(
        "--cube",
        help="R|Write CUBE file during production run (can produce large file) instead of BQB.",
        dest="cube",
        action="store_true",
        default=False,
    )
    p.add_argument(
        "--timestep",
        type=float,
        help="R|Time step for the simulation in fs.",
        default=0.5,
        dest="timestep",
        action=action_in_range(0.1, 4.0),
        metavar="TIME",
    )
    p.add_argument(
        "--dftu",
        help="R|Use DFT+U.\nRequires three additional arguments per atom type (space separated):\nAtom type, orbital angular momentum quantum number, U-J value in eV.",
        nargs="+",
        dest="dftu",
        metavar="ATOM, L, UJ",
        default=None,
        action=action_check_dftu(),
    )
    p.add_argument(
        "--efield",
        type=str,
        help="R|Add a periodic electric field in given directions.",
        default=None,
        dest="efield",
        choices=["x", "y", "z", "xy", "xz", "yz", "xyz"],
    )
    p.add_argument(
        "--e-conv-equi",
        type=float,
        metavar="CUTOFF",
        dest="e_conv",
        help="R|Energy convergence criterion in Hartree.",
        default=1.0e-6,
        action=action_not_more_than(1e-4),
    )
    p.add_argument(
        "--e-conv-relax",
        type=float,
        metavar="CUTOFF",
        dest="e_conv",
        help="R|Energy convergence criterion in Hartree.",
        default=1.0e-6,
        action=action_not_more_than(1e-4),
    )
    p.add_argument(
        "--e-conv-prod",
        type=float,
        metavar="CUTOFF",
        dest="e_conv",
        help="R|Energy convergence criterion in Hartree.",
        default=1.0e-6,
        action=action_not_more_than(1e-4),
    )
    p.add_argument(
        "--ensemble",
        type=str,
        dest="ensemble",
        help="R|Thermodynamic ensemble for production run.",
        default="nvt",
        choices=["nvt", "nve"],
    )
    p.add_argument(
        "--field-strength",
        type=float,
        metavar="STRENGTH",
        help="R|Strength of the electric field in a.u.",
        default=5.0e-3,
        dest="efield_strength",
        action=action_not_less_than(0.0),
    )
    p.add_argument(
        "--func",
        type=str,
        help="R|Density functional.",
        default="revpbe",
        dest="func",
        choices=["blyp", "bp", "pade", "pbe", "revpbe", "scan", "r2scan", "xtb"],
    )
    p.add_argument(
        "--mult",
        type=int,
        metavar="N",
        help="R|Multiplicity of the system.",
        default=1,
        dest="mult",
        action=action_not_less_than(1),
    )
    p.add_argument(
        "--n-bqb",
        type=int,
        metavar="N",
        help="R|Number of bqb files to generate.",
        default=6,
        dest="n_bqb",
        action=action_not_less_than(1),
    )
    p.add_argument(
        "--no-copy",
        help="R|Do not copy trajectory file to project directory.",
        action="store_true",
        default=False,
        dest="no_copy",
    )
    p.add_argument(
        "--no-equi",
        help="R|Do not perform equilibration as part of an 'aimd' type calculation.",
        action="store_true",
        default=False,
        dest="no_equi",
    )
    p.add_argument(
        "--no-relax",
        help="R|Do not perform relaxation as part of an 'aimd' type calculation.",
        action="store_true",
        default=False,
        dest="no_relax",
    )
    p.add_argument(
        "--no-prod",
        help="R|Do not perform production run as part of an 'aimd' type calculation.",
        action="store_true",
        default=False,
        dest="no_prod",
    )
    p.add_argument(
        "-o",
        "--overwrite",
        help="R|Overwrite existing project directory.",
        action="store_true",
        default=False,
        dest="overwrite",
    )
    p.add_argument(
        "--opt-level",
        type=str,
        help="R|Level of geometry optimization convergence.",
        default="normal",
        choices=["loose", "normal", "tight"],
        dest="opt_level",
    )
    p.add_argument(
        "--pbc",
        type=str,
        help="R|Periodic boundary conditions.",
        default="xyz",
        dest="pbc",
        choices=["xyz", "none"],
    )
    p.add_argument(
        "-q",
        type=str,
        help="R|Cluster/queue to submit the job to.",
        default="noctua2",
        dest="queue",
        choices=["noctua2", "bonna"],
    )
    p.add_argument(
        "--reftraj",
        type=is_file,
        metavar="FILE",
        help="R|Reference trajectory file to calculate the spectrum from.",
        dest="reftraj",
    )
    p.add_argument(
        "--start-from",
        type=int,
        metavar="N",
        help="R|Start processing trajectory from this step.",
        default=1,
        dest="start_from",
        action=action_not_less_than(1),
    )
    p.add_argument(
        "--spec",
        type=str,
        dest="spectrum",
        help="R|Type of spectrum to calculate.",
        default="ir",
        choices=["ir", "vcd", "raman", "roa", "dipoles"],
    )
    p.add_argument(
        "--steps-bqb",
        type=int,
        metavar="N",
        help="R|Number of steps per bqb file (without overlap).",
        default=10000,
        dest="steps_bqb",
        action=action_not_less_than(1),
    )
    p.add_argument(
        "--steps-equi",
        type=int,
        metavar="N",
        help="R|Number of equilibration steps.",
        default=20000,
        action=action_not_less_than(1),
    )
    p.add_argument(
        "--steps-relax",
        type=int,
        metavar="N",
        help="R|Number of relaxation steps.",
        default=10000,
        action=action_not_less_than(1),
    )
    p.add_argument(
        "--steps-prod",
        type=int,
        metavar="N",
        help="R|Number of production steps.",
        default=60000,
        action=action_not_less_than(1),
    )
    p.add_argument(
        "--thermo",
        type=str,
        help="R|Thermostat.",
        default="NOSE",
        choices=["nose", "csvr"],
    )
    p.add_argument(
        "--t-equi",
        type=float,
        metavar="TEMP",
        help="R|Equilibration temperature in K.",
        default=400.0,
        action=action_not_less_than(250),
    )
    p.add_argument(
        "--t-relax",
        type=float,
        metavar="TEMP",
        help="R|Relaxation temperature in K.",
        default=350.0,
        action=action_not_less_than(250),
    )
    p.add_argument(
        "--t-prod",
        type=float,
        metavar="TEMP",
        help="R|Production temperature in K.",
        default=350.0,
        action=action_not_less_than(250),
    )
    p.add_argument(
        "--type",
        type=str,
        help="R|Type of calculation to perform.\nAIMD: AIMD simulation.\nBQB: BQB file production.\nENERGY: Single point energy calculation.\nADAPT-SAMPL: Adaptive sampling.\nGEOOPT: Geometry optimization.",
        dest="type",
        choices=["aimd", "bqb", "energy", "adapt-sampl", "geoopt"],
        default="aimd",
    )
    p.add_argument(
        "--uks",
        "--lsd",
        help="R|Use Unrestricted Kohn-Sham calculation, also known als Local Spin Density.\nIs automatically set for multiplicity > 1.",
        default=False,
        action="store_true",
        dest="uks",
    )
    p.add_argument(
        "--vel",
        type=is_file,
        metavar="FILE",
        help="R|Initial velocities file in Bohr/au_time.",
        dest="velocity",
    )
    p.add_argument(
        "-w",
        "--wannier",
        help="R|Calculate Wannier functions in production run.",
        default=False,
        action="store_true",
        dest="wannier",
    )
    p.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + str(__version__),
        help="Show program's version number and exit.",
    )
    p.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )

    return p
