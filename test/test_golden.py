"""
Golden-file tests: run the full setup for representative option sets and compare every
generated file with a stored reference in ``test/data/golden/<case>/``.

The references record the current behavior. They guard against unintended changes, for
example when the input generation is rewritten. After an intentional change, regenerate
them with ``pytest test/test_golden.py --update-golden`` and review the diff in git.

CP2K inputs are compared by content, not by text: both files are parsed with
cp2k-input-tools, which also validates them against the CP2K input schema. Keyword and
section order, indentation, letter case and number formatting therefore do not matter.
Other files (runscripts, copied coordinates) must match exactly.
"""

from __future__ import annotations

import functools
import io
import shutil
from pathlib import Path
from typing import Any

import pytest
from cp2k_input_tools.parser import CP2KInputParserSimplified

from aimd_setup.cli import console_entry_point

DATA_DIR = Path(__file__).parent / "data"
INPUT_DIR = DATA_DIR / "inputs"
GOLDEN_DIR = DATA_DIR / "golden"

WATER = str(INPUT_DIR / "water.xyz")
FEOH = str(INPUT_DIR / "feoh.xyz")
TRAJ = str(INPUT_DIR / "water_traj.xyz")
VEL = str(INPUT_DIR / "water_vel.txt")

# each case covers a distinct path through the setup; the project name is the case name
# fmt: off
CASES: dict[str, list[str]] = {
    # eq -> relax -> prod with all defaults, box size read from the xyz file
    "aimd_default": ["-c", WATER],
    # prod only after relax, all density outputs, Wannier centers, periodic E-field,
    # short production run (BQB history 1)
    "aimd_outputs": [
        "-c", WATER, "--no-equi", "--bqb", "--cube", "--voronoi", "--wannier",
        "--efield", "z", "--steps-prod", "5",
    ],
    # NVE production with initial velocities, non-periodic, open shell
    "aimd_nve_cluster": [
        "-c", WATER, "--no-relax", "--ensemble", "nve", "--vel", VEL,
        "--pbc", "none", "--mult", "2",
    ],
    # r2SCAN with TZV2P basis and a non-default seed
    "aimd_r2scan": [
        "-c", WATER, "--no-equi", "--no-relax", "--func", "r2scan",
        "--basis", "tzv2p", "--seed", "1234",
    ],
    # single point with DFT+U, charge, multiplicity, cube output, two nodes on bonna
    "energy_dftu": [
        "-c", FEOH, "-b", "10.0", "--type", "energy", "--dftu", "Fe", "2", "4.0",
        "--mult", "5", "--chrg", "1", "--cube",
        "-q", "bonna", "--cp2k-version", "2024.3", "--cpu", "64",
    ],
    # geometry optimization with xTB on berta2
    "geoopt_xtb": [
        "-c", WATER, "--type", "geoopt", "--func", "xtb", "--opt-level", "tight",
        "-q", "berta2", "--cp2k-version", "2024.3", "--cpu", "32",
    ],
    # IR spectrum: two BQB chunks from a reference trajectory, with Voronoi output
    "bqb_ir": [
        "-c", WATER, "--type", "bqb", "--reftraj", TRAJ, "--n-bqb", "2",
        "--start-from", "100", "--voronoi",
    ],
    # Raman spectrum: one subdirectory per field direction, on marvin
    "bqb_raman": [
        "-c", WATER, "--type", "bqb", "--reftraj", TRAJ, "--spec", "raman",
        "-q", "marvin", "--cp2k-version", "2025.2", "--cpu", "192",
    ],
    # adaptive sampling: two-step production run started from velocities
    "adapt_sampl": ["-c", WATER, "--type", "adapt-sampl", "--vel", VEL],
}
# fmt: on


def relative_files(directory: Path) -> list[Path]:
    """List all files below a directory, relative to it and sorted.

    Parameters
    ----------
    directory : Path
        Directory to search.

    Returns
    -------
    list[Path]
        Sorted file paths relative to ``directory``.
    """
    return sorted(
        p.relative_to(directory) for p in directory.rglob("*") if p.is_file()
    )


def parse_cp2k_input(path: Path) -> tuple[dict[str, Any], list[str]]:
    """Parse and validate a CP2K input file with cp2k-input-tools.

    The parser of cp2k-input-tools (0.9.3) rejects the valid keyword
    ``IONS+CENTERS`` because it stops reading a keyword name at ``+``. Such lines are
    therefore removed before parsing and returned separately for comparison.

    Parameters
    ----------
    path : Path
        CP2K input file.

    Returns
    -------
    tuple[dict[str, Any], list[str]]
        The parsed input tree, and the stripped ``IONS+CENTERS`` lines.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    ions_centers = [
        line.strip()
        for line in lines
        if line.strip().upper().startswith("IONS+CENTERS")
    ]
    kept = [
        line
        for line in lines
        if not line.strip().upper().startswith("IONS+CENTERS")
    ]
    tree = cp2k_parser().parse(io.StringIO("\n".join(kept)))
    return tree, ions_centers


@functools.cache
def cp2k_parser() -> CP2KInputParserSimplified:
    """Create the parser once; loading the CP2K schema takes several seconds.

    Returns
    -------
    CP2KInputParserSimplified
        Parser that validates against the schema bundled with cp2k-input-tools.
    """
    return CP2KInputParserSimplified()


@pytest.mark.parametrize("case", CASES)
def test_golden(
    case: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    update_golden: bool,
) -> None:
    """Generated project directory matches the stored reference file by file."""
    monkeypatch.chdir(tmp_path)
    assert console_entry_point(["-p", case, *CASES[case]]) == 0

    generated = tmp_path / case
    golden = GOLDEN_DIR / case

    if update_golden:
        if golden.exists():
            shutil.rmtree(golden)
        shutil.copytree(generated, golden)
        pytest.skip(f"Updated golden files for '{case}'.")

    assert (
        golden.is_dir()
    ), f"No golden files for '{case}'. Run with --update-golden."
    assert relative_files(generated) == relative_files(golden)
    for rel in relative_files(golden):
        if rel.suffix == ".inp":
            same = parse_cp2k_input(generated / rel) == parse_cp2k_input(
                golden / rel
            )
        else:
            # read_text normalizes line endings, so this also holds on Windows
            same = (generated / rel).read_text(encoding="utf-8") == (
                golden / rel
            ).read_text(encoding="utf-8")
        assert same, f"{case}/{rel} differs from the golden file"


def test_unsupported_element_exits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An element without pseudopotential data stops the setup."""
    monkeypatch.chdir(tmp_path)
    coord = tmp_path / "xe.xyz"
    coord.write_text("1\n10.0 10.0 10.0\nXe 0.0 0.0 0.0\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="Atom type Xe not supported"):
        console_entry_point(["-p", "xe", "-c", str(coord)])


def test_dftu_element_not_in_coord_exits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """DFT+U for an element missing from the coordinates stops the setup."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit, match="Atom type Fe not present"):
        console_entry_point(
            [
                "-p",
                "u",
                "-c",
                WATER,
                "--type",
                "energy",
                "--dftu",
                "Fe",
                "2",
                "4.0",
            ]
        )


def test_unknown_cp2k_version_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A CP2K version that exists, but not on the chosen cluster, is rejected."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="CP2K version 2025.1 not available"):
        console_entry_point(
            ["-p", "v", "-c", WATER, "-q", "bonna", "--cp2k-version", "2025.1"]
        )


def test_toml_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Options from a TOML file are used, with '-' and '_' treated alike."""
    monkeypatch.chdir(tmp_path)
    config = tmp_path / "config.toml"
    config.write_text(
        f'project = "toml"\ncoord = {WATER!r}\nboxsize = [10.0, 11.0, 12.0]\n'
        'type = "energy"\nmult = 3\n',
        encoding="utf-8",
    )
    assert console_entry_point(["-i", str(config)]) == 0
    energy = (tmp_path / "toml" / "energy.inp").read_text(encoding="utf-8")
    assert "ABC 10.0 11.0 12.0" in energy
    assert "MULTIPLICITY 3" in energy


@pytest.mark.parametrize(
    "func", ["blyp", "bp", "pade", "pbe", "revpbe", "pbe0", "scan", "r2scan"]
)
def test_functional_input_valid(
    func: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every density functional gives a valid input, also with an E-field."""
    monkeypatch.chdir(tmp_path)
    argv = ["-p", func, "-c", WATER, "--type", "energy", "--func", func]
    assert console_entry_point([*argv, "--efield", "x"]) == 0
    tree, _ = parse_cp2k_input(tmp_path / func / "energy.inp")
    assert "xc_functional" in tree["force_eval"]["dft"]["xc"]
    assert tree["force_eval"]["dft"]["periodic_efield"]["intensity"] > 0
