# Part of the AIMD setup tool
# Originally written by Marvin Friede for dxtb 
# Adapted by Tom Frömbgen
# Last modified 2023-05-05

"""
Parser for command line options.
"""

#############################################

# module imports
import argparse
from pathlib import Path

#############################################

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
def action_not_less_than(min_value: float = 0.0):
    class CustomActionLessThan(argparse.Action):
        """
        Custom action for limiting possible input values. Raise error if value is smaller than min_value.
        """

        def __call__(
            self,
            p: argparse.ArgumentParser,
            args: argparse.Namespace,
            values: list[float | int] | float | int,
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

def action_not_more_than(max_value: float = 0.0):
    class CustomActionMoreThan(argparse.Action):
        """
        Custom action for limiting possible input values. Raise error if value is larger than max_value.
        """

        def __call__(
            self,
            p: argparse.ArgumentParser,
            args: argparse.Namespace,
            values: list[float | int] | float | int,
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

def action_in_range(min_value: float = 0.0, max_value: float = 1.0):
    class CustomActionInRange(argparse.Action):
        """
        Custom action for limiting possible input values in a range. Raise error if value is not in range [min_value, max_value].
        """

        def __call__(
            self,
            p: argparse.ArgumentParser,
            args: argparse.Namespace,
            values: list[float | int] | float | int,
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
def parser(name: str = "aimd-setup", **kwargs) -> argparse.ArgumentParser:
    """
    Parses the command line arguments.

    Returns
    -------
    argparse.ArgumentParser
        Container for command line arguments.
    """

    p = argparse.ArgumentParser(
        prog="aimd-setup",
        description="Script to setup AIMD simulations or BQB file productions with CP2K.",
        epilog="Written for the Kirchner group by Tom Frömbgen. Internal use only.",
        formatter_class=lambda prog: Formatter(prog, max_help_position=60),
        add_help=False,
        **kwargs,
    )
    p.add_argument(
        "project", 
        type=str, 
        help="R|Name of the project. A directory with this name will be created.",
    )
    p.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )
    p.add_argument(
        "--basis",
        type=str, 
        help="R|Basis set.", 
        default="DZVP", 
        dest="basis",
        choices=["svz", "dzvp", "tzvp", "tzv2p", "tzv2px"]
    )
    p.add_argument(
        "--boxsize", 
        type=float, 
        dest="boxsize",
        help="R|Box edge length in Angstrom.", 
        metavar="LENGTH", 
        default=10.0,
        action=action_not_less_than(5.0),
    )
    p.add_argument(
        "-c",
        "--coord-file", 
        type=is_file, 
        help="R|Coordinate file (in xyz format).",
        dest="coord",
        metavar="FILE",
        )
    p.add_argument(
        "--e-conv", 
        type=float, 
        metavar="CUTOFF",
        dest="e_conv", 
        help="R|Energy convergence criterion in Hartree.", 
        default=1.0e-6,
        action=action_not_more_than(1e-4),
    )
    p.add_argument(
        "--func", 
        type=str, 
        help="R|Density functional.", 
        default="BLYP", 
        dest="func",
        choices=["blyp", "bp", "pade", "pbe", "revpbe"],
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
        "-o",
        "--overwrite", 
        help="R|Overwrite existing project directory.",
        action="store_true", 
        default=False, 
        dest="overwrite",
    )
    p.add_argument(
        "-q",
        "--queue", 
        type=str, 
        metavar="QUEUE",
        help="R|Cluster/queue to submit the job to.", 
        default="hedy", 
        dest="queue", 
        choices=["hedy", "iris", "noctua2"],
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
        default=None,
        choices=["ir", "vcd", "raman", "roa"],
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
        action=action_not_less_than(1000),
    )
    p.add_argument(
        "--steps-relax", 
        type=int, 
        metavar="N",
        help="R|Number of relaxation steps.", 
        default=10000,
        action=action_not_less_than(1000),
    )
    p.add_argument(
        "--steps-prod", 
        type=int, 
        metavar="N",
        help="R|Number of production steps.", 
        default=60000,
        action=action_not_less_than(1000),
    )
    p.add_argument(
        "--type", 
        type=str, 
        help="R|Type of calculation to perform.", 
        dest="type",
        choices=["aimd", "bqb", "single-point"], 
        default="aimd",
    )
    p.add_argument(
        "--thermo", 
        type=str, 
        metavar="THERMO",
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
        action=action_not_less_than(250)
    )

    p.add_argument(
        "--t-relax", 
        type=float, 
        metavar="TEMP",
        help="R|Relaxation temperature in K.", 
        default=350.0,
        action=action_not_less_than(250)
    )

    p.add_argument(
        "--t-prod", 
        type=float, 
        metavar="TEMP",
        help="R|Production temperature in K.", 
        default=350.0,
        action=action_not_less_than(250)
    )
    p.add_argument(
        "-w",
        "--wannier",
        help="R|Calculate Wannier functions in production run.",
        default=False, 
        action="store_true", 
        dest="wannier",
    )
    ##############################
    
    # p.add_argument(
    #     "--version",
    #     action="store_true",
    #     default=argparse.SUPPRESS,
    #     help="Show version and exit.",
    # )
    # p.add_argument(
    #     "--chrg",
    #     action=action_not_less_than(-10.0),
    #     type=int,
    #     default=defaults.CHRG,
    #     nargs="+",
    #     help="R|Molecular charge.",
    # )
    # p.add_argument(
    #     "--spin",
    #     "--uhf",
    #     action=action_not_less_than(0.0),
    #     type=int,
    #     default=defaults.SPIN,
    #     nargs="+",
    #     help="R|Molecular spin.",
    # )
    # p.add_argument(
    #     "--exclude",
    #     type=str,
    #     default=defaults.EXCLUDE,
    #     choices=defaults.EXCLUDE_CHOICES,
    #     nargs="+",
    #     help="R|Turn off energy contributions.",
    # )
    # p.add_argument(
    #     "--etemp",
    #     action=action_not_less_than(0.0),
    #     type=float,
    #     default=defaults.ETEMP,
    #     help="R|Electronic Temperature in K.",
    # )
    # p.add_argument(
    #     "--fermi_maxiter",
    #     type=int,
    #     default=defaults.FERMI_MAXITER,
    #     help="R|Maximum number of iterations for Fermi smearing.",
    # )
    # p.add_argument(
    #     "--fermi_energy_partition",
    #     type=str,
    #     default=defaults.FERMI_FENERGY_PARTITION,
    #     choices=defaults.FERMI_FENERGY_PARTITION_CHOICES,
    #     help="R|Partitioning scheme for electronic free energy.",
    # )
    # p.add_argument(
    #     "--maxiter",
    #     type=int,
    #     default=defaults.MAXITER,
    #     help="R|Maximum number of SCF iterations.",
    # )
    # p.add_argument(
    #     "-v",
    #     "--verbosity",
    #     type=int,
    #     default=defaults.VERBOSITY,
    #     help="R|Verbosity level of printout.",
    # )
    # p.add_argument(
    #     "--method",
    #     type=str,
    #     default=defaults.METHOD,
    #     choices=defaults.METHOD_CHOICES,
    #     help="R|Method for calculation.",
    # )
    # p.add_argument(
    #     "--guess",
    #     type=str,
    #     default=defaults.GUESS,
    #     choices=defaults.GUESS_CHOICES,
    #     help="R|Model for initial charges.",
    # )
    # p.add_argument(
    #     "--grad",
    #     action="store_true",
    #     help="R|Whether to compute gradients for positions w.r.t. energy.",
    # )
    # p.add_argument(
    #     "--profile",
    #     action="store_true",
    #     help=(
    #         "R|Profile the program.\n"
    #         "Creates 'dxtb.profile' that can be analyzed with 'snakeviz'."
    #     ),
    # )
    # p.add_argument(
    #     "--dir",
    #     nargs="?",
    #     type=is_dir,  # manual validation
    #     help="R|Directory with all files. Searches recursively.",
    # )
    # p.add_argument(
    #     "--filetype",
    #     type=str,
    #     choices=["xyz", "tm", "tmol", "turbomole", "json", "qcschema"],
    #     help="R|Explicitly set file type of input.",
    # )
    # p.add_argument(
    #     "file",
    #     nargs="?",
    #     type=is_file,  # manual validation
    #     help="R|Path to coordinate file.",
    # )

    return p
