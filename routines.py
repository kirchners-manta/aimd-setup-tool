#!/usr/bin/python3

# Part of the AIMD setup tool
# Written by Tom Frömbgen
# Last modified 2023-01-23

import sys
import re

# Modify the CP2K input files for the AIMD simulation


def adjust_cp2k_input_aimd(cp2k_infiles: list, data: dict) -> None:
    """Adjust the CP2K input files for an AIMD simulation

    Parameters
    ----------
    cp2k_infiles : list
        List of the CP2K input files as strings
    data : dict
        Dictionary with the data from the command line arguments, including default values
    """

    # check if this function was called for the correct type of calculation
    if data["type"] != "aimd":
        sys.exit(
            "Error: adjust_cp2k_input_aimd() was called for the wrong type of calculation.")

    for i, file in enumerate(cp2k_infiles):

        # open the file
        with open(file, "r") as f:
            # the file is read into a list of lines, the string is changed and the file is written again
            lines = []
            lines = f.read()

            # for the geometry optimization: adjust project name, box length, coord file, density functional, basis set, pseudopotential
            if i == 0:

                lines = re.sub("\$\{PROJECT_NAME\}",
                               str(data["project"]), lines)
                lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
                lines = re.sub("\$\{SIMBOX_XYZ\}", str(data["coord"]), lines)
                lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
                lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
                lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)
                # if REVPBE is used, add an addtional line to the CP2K input file
                # in the &XC_FUNCTIONAL section, add the line: PARAMETRIZATION REVPBE
                if data["func"] == "REVPBE":
                    lines = re.sub(
                        "&XC_FUNCTIONAL REVPBE", "&XC_FUNCTIONAL PBE\n\tPARAMETRIZATION REVPBE", lines)

                with open(file, "w") as g:
                    g.writelines(lines)

            # for the equilibration: adjust project name, box length, coord file, thermostat, temperature and number of steps, density functional, basis set, pseudopotential
            elif i == 1:

                lines = re.sub("\$\{PROJECT_NAME\}",
                               str(data["project"]), lines)
                lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
                lines = re.sub("\$\{SIMBOX_XYZ\}", str(data["coord"]), lines)
                lines = re.sub("\$\{THERMO\}", str(data["thermo"]), lines)
                lines = re.sub("\$\{TEMP\}", str(data["t_equi"]), lines)
                lines = re.sub("\$\{NSTEPS\}", str(data["steps_equi"]), lines)
                lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
                lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
                lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)
                # if REVPBE is used, add an addtional line to the CP2K input file
                # in the &XC_FUNCTIONAL section, add the line: PARAMETRIZATION REVPBE
                if data["func"] == "REVPBE":
                    lines = re.sub(
                        "&XC_FUNCTIONAL REVPBE", "&XC_FUNCTIONAL PBE\n\tPARAMETRIZATION REVPBE", lines)

                with open(file, "w") as g:
                    g.writelines(lines)

            # for the relaxation: adjust project name, box length, coord file, thermostat, temperature and number of steps, density functional, basis set, pseudopotential
            elif i == 2:

                lines = re.sub("\$\{PROJECT_NAME\}",
                               str(data["project"]), lines)
                lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
                lines = re.sub("\$\{SIMBOX_XYZ\}", str(data["coord"]), lines)
                lines = re.sub("\$\{THERMO\}", str(data["thermo"]), lines)
                lines = re.sub("\$\{TEMP\}", str(data["t_relax"]), lines)
                lines = re.sub("\$\{NSTEPS\}", str(data["steps_relax"]), lines)
                lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
                lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
                lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)
                # if REVPBE is used, add an addtional line to the CP2K input file
                # in the &XC_FUNCTIONAL section, add the line: PARAMETRIZATION REVPBE
                if data["func"] == "REVPBE":
                    lines = re.sub(
                        "&XC_FUNCTIONAL REVPBE", "&XC_FUNCTIONAL PBE\n\tPARAMETRIZATION REVPBE", lines)

                with open(file, "w") as g:
                    g.writelines(lines)

            # for the production: adjust project name, box length, coord file, thermostat, temperature and number of steps, density functional, basis set, pseudopotential and Wannier if desired
            elif i == 3:

                lines = re.sub("\$\{PROJECT_NAME\}",
                               str(data["project"]), lines)
                lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
                lines = re.sub("\$\{SIMBOX_XYZ\}", str(data["coord"]), lines)
                lines = re.sub("\$\{THERMO\}", str(data["thermo"]), lines)
                lines = re.sub("\$\{TEMP\}", str(data["t_prod"]), lines)
                lines = re.sub("\$\{NSTEPS\}", str(data["steps_prod"]), lines)
                lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
                lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
                lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)
                # if REVPBE is used, add an addtional line to the CP2K input file
                # in the &XC_FUNCTIONAL section, add the line: PARAMETRIZATION REVPBE
                if data["func"] == "REVPBE":
                    lines = re.sub(
                        "&XC_FUNCTIONAL REVPBE", "&XC_FUNCTIONAL PBE\n\tPARAMETRIZATION REVPBE", lines)

                # if wannier is requested, adjust the input file
                # remove the comment symbols (#) from the wannier section
                if data["wannier"] == True:
                    
                    # set the pointer to the beginning of the file
                    f.seek(0)
                    lines = f.readlines()
                    
                    for j, line in enumerate(lines):

                        # find start of wannier section
                        if "&LOCALIZE" in line:
                            
                            # remove comment symbols from the following lines until the end of the section
                            for k in range(j, len(lines)):
                                if "&END LOCALIZE" in lines[k]:
                                    lines[k] = lines[k][1:]
                                    break
                                # remove first comment symbol
                                else:
                                    lines[k] = lines[k][1:]
                                    
                with open(file, "w") as g:
                    g.writelines(lines)

# modify the CP2K input file for a single point calculation


def adjust_cp2k_input_sp(cp2k_infiles: list, data: dict) -> None:
    """Adjust the CP2K input file for a single point calculation

    Parameters
    ----------
    cp2k_infiles : str
        filename of the CP2K input file
    data : dict
        dictionary containing the data for the calculation
    """

    # check if this function was called for the correct type of calculation
    if data["type"] != "single-point":
        sys.exit(
            "Error: adjust_cp2k_input_sp() was called for the wrong type of calculation.")

    for i, file in enumerate(cp2k_infiles):

        with open(file, "r") as f:

            # the file is read into a list of lines, the string is changed and the file is written again
            lines = []
            lines = f.read()
            lines = re.sub("\$\{PROJECT_NAME\}",
                           str(data["project"]), lines)
            lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
            lines = re.sub("\$\{COORD_FILE\}", str(data["coord"]), lines)
            lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
            lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
            lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)
            lines = re.sub("\$\{ENERGY_CUTOFF\}", str(data["e_conv"]), lines)
            lines = re.sub("\$\{ENERGY_CUTOFF_2\}",
                           str(data["e_conv"]**2), lines)
            # if REVPBE is used, add an addtional line to the CP2K input file
            # in the &XC_FUNCTIONAL section, add the line: PARAMETRIZATION REVPBE
            if data["func"] == "REVPBE":
                lines = re.sub(
                    "&XC_FUNCTIONAL REVPBE", "&XC_FUNCTIONAL PBE\n\tPARAMETRIZATION REVPBE", lines)

            with open(file, "w") as g:
                g.writelines(lines)


def adjust_runscript(runscript: str, project: str, queue: str) -> None:
    """Adjust the runscript for the queue system

    Parameters
    ----------
    runscript : str
        filename of the runscript
    project : str
        project name
    queue : str
        queue system to execute the calculation
    """

    # open the file
    with open(runscript, "r") as f:

        # the file is read into a list of lines, the string is changed and the file is written again
        lines = []
        lines = f.read()
        lines = re.sub("PROJECT_NAME", project, lines)
        lines = re.sub("QUEUE_NAME", queue, lines)

        with open(runscript, "w") as g:
            g.writelines(lines)
