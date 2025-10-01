# AIMD Setup Tool
---

![Python versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This repository offers a tool to set up ab initio molecular dynamics (AIMD) simulations and subsequent calculations of vibrational spectra using the [CP2K](https://www.cp2k.org/) software package.
It is primarily written for the [group of Barbara Kirchner](https://www.chemie.uni-bonn.de/kirchner/de/startseite) at the University of Bonn and published under the [MIT license](./LICENSE).

## Installation

The tool can be installed using `pip`:

```bash
git clone git@github.com:kirchners-manta/aimd-setup-tool.git
cd aimd-setup-tool
pip install .
```

## Usage

Currently, the tool has features to set up AIMD simulations and subsequent calculations of vibrational spectra in CP2K.
It can be called from the command line as
```bash
aimd_setup [OPTIONS]
```
Various options are available to customize the setup.
A full list of options can be obtained by calling
```bash
aimd_setup -h
```
Two options are always required: `-p` (project name) and `-c` (input coordinate file in `.xyz` format).
A new directory will be created for the project, using the specified name, and the input coordinate file will be copied to this directory.
The box geometry is also required via the `-b` (box length) option, unless the box size is specified in the second line of the coordinate file.
If the box is cubic, a single value can be given, otherwise a list of three values (box lengths in x, y, and z direction) has to be provided.
Boxes with non-orthogonal angles are currently not supported.
Thus, a very simple call of the program could look like this:
```bash
aimd_setup -p my_project -c input.xyz -b 10.0
```
As this program features an ever-increasing number of options (still much less than what CP2K allows), and it can be cumbersome to specify many options on the command line, all options can also be specified in a [TOML](https://toml.io/en/) configuration file, which can be used by calling
```bash
aimd_setup -i my_aimd_config.toml
```
**Note:** Options specified in the configuration file will overwrite options specified on the command line and default options.
An exemplary configuration file could look like this:
```toml
project = "test"
coord   = "input.xyz"
boxsize = [10.0, 11.0, 12.0]
```
Also note that the program will print a list of options used for the setup to the terminal - checking this list is a good idea to ensure that the intended options were used.

One of the most important options is the `--type` option, which specifies the type of calculation to be set up.
Currently, four types are implemented:
- `aimd`: AIMD simulation (default).
- `bqb`: Calculation of vibrational spectra from an existing AIMD trajectory.
- `energy`: Single-point energy calculation.
- `geoopt`: Geometry optimization.
If the `aimd` type is chosen, three input files will be created in the project directory:
- `eq.inp`: First equilibration run at elevated temperature.
- `relax.inp`: Second equilibration run at target temperature (which we call relaxation here, not to be confused with geometry optimization).
- `prod.inp`: Production run at target temperature.
These runs can be further customized using various options, e.g., to set the length of each run or the target temperature (see `aimd_setup -h` for details).
Either of these runs can also be skipped using the `--no-equi` or `--no-relax` or `--no-prod` flags, respectively.

The cluster on which the calculations will be run can be specified using the `-q`/`--queue` option and the CP2K version using the `--cp2k-version` option.

## Contributors

- [Tom Frömbgen](https://github.com/tomfroembgen): [tomfroe@uni-bonn.de](mailto:tomfroe@uni-bonn.de)
