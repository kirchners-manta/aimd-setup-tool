# AIMD Setup Tool
---

![Python versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This repository offers a tool to set up ab initio molecular dynamics (AIMD) simulations and subsequent calculations of vibrational spectra using the [CP2K](https://www.cp2k.org/) software package.
It is primarily written for the [group of Barbara Kirchner](https://www.chemie.uni-bonn.de/kirchner/de/startseite) at the University of Bonn and published under the [MIT license](./LICENSE).

## Installation

The tool can be installed using `pip`:

```bash
git clone git@github.com:tomfroembgen/aimd-setup-tool.git
```
or
```bash
git clone git@github.com:kirchners-manta/aimd-setup.git
```
and then
```bash
cd aimd-setup-tool
pip install .
```

## Usage

Currently, the tool has features to set up AIMD simulations and subsequent calculations of vibrational spectra in CP2K.
It can be called from the command line as
```bash
aimd_setup -p PROJECT -c FILE -b LENGTH [OPTIONS]
```
where `PROJECT` is the name of the directory to be created, `FILE` is the input coordinate file for the AIMD simulation, and `LENGTH` is the box length of the simulation cell.
Various options are available to customize the setup.
A full list of options can be obtained by calling
```bash
aimd_setup -h
```
All options can also be specified in a configuration file, which can be created by calling
```bash
aimd_setup -i FILE
```
where `FILE` is the name of the configuration file.
**Note:** Options specified in the configuration file will overwrite options specified on the command line and default options.
