# AIMD Setup Tool
---

![Python versions](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)
![Tests](https://github.com/tomfroembgen/python-project/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/tomfroembgen/python-project/branch/main/graph/badge.svg?token=UEKDZY459S)](https://codecov.io/gh/tomfroembgen/python-project)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/tomfroembgen/python-project/main.svg)](https://results.pre-commit.ci/latest/github/tomfroembgen/python-project/main)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This repository offers a tool to set up ab initio molecular dynamics (AIMD) simulations and subsequent calculations of vibrational spectra using the [CP2K](https://www.cp2k.org/) software package. 
It is primarily written for the [group of Barbara Kirchner](https://www.chemie.uni-bonn.de/kirchner/de/startseite) at the University of Bonn and published under the [MIT license](./LICENSE).

## Installation

The tool can be installed using `pip`:

```bash
git clone git@github.com:tomfroembgen/aimd-setup-tool.git
cd aimd-setup-tool
pip install .
```

## Usage

Currently, the tool has features to set up AIMD simulations and subsequent calculations of vibrational spectra in CP2K.
It can be called from the command line as
```bash
aimd_setup [OPTIONS] project_name
```
where `project_name` is the name of the directory to be created.
Various options are available to customize the setup.
A full list of options can be obtained by calling
```bash
aimd_setup -h
```
