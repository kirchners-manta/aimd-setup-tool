# Part of the AIMD setup tool

"""
Functions to adjust input files for the AIMD setup tool.
"""

#############################################

from __future__ import annotations

import os
import re
import sys
from typing import Any


# Copy the CP2K data files and the runscript to a directory
def copy_cp2k_data_and_runscript(
    template_dir: str, project_dir: str, runscript: str
) -> None:
    """Copy the CP2K data files and the runscript to a directory

    Parameters
    ----------
    template_dir : str
        path to the directory containing the template files (CP2K data files and runscript)
    project_dir : str
        path to the directory where the files should be copied to
    runscript : str
        name of the runscript to be used
    """

    # copy the CP2K data files
    os.system("cp " + template_dir + "/../cp2k-datafiles/* " + project_dir)

    # copy the runscript
    os.system("cp " + template_dir + "/../runscripts/" + runscript + " " + project_dir)


# remove comments from the CP2K input files and remove all lines that only contain whitespace
def remove_comments_and_whitespace(llist: str) -> str:
    """Takes a string and removes all comments and all lines that only contain whitespace

    Parameters
    ----------
    llist : str
        string to be modified
    """

    # remove all comments from the list elements, a comment starts with a #
    # do not remove the top line comment
    llist = re.sub("(?<!^)#.*", "", llist)
    # remove all lines that only contain whitespace
    llist = re.sub("^\s*\n", "", llist, flags=re.MULTILINE)

    return llist


# special adjustment for revPBE functional
def revpbe_adjustment(llist: str) -> str:
    """Takes a string and adds an additional line to the CP2K input file if the REVPBE functional is used

    Parameters
    ----------
    llist : str
        string to be modified
    """

    # if REVPBE is used, add an addtional line to the CP2K input file
    # in the &XC_FUNCTIONAL section, add the line: PARAMETRIZATION REVPBE
    if "REVPBE" in llist:
        llist = re.sub(
            "&XC_FUNCTIONAL REVPBE",
            "&XC_FUNCTIONAL\n\t\t\t\t&PBE\n\t\t\t\t\tPARAMETRIZATION REVPBE\n\t\t\t\t&END PBE",
            llist,
        )

    return llist


# special adjustment for SCAN functional
def scan_adjustment(llist: str) -> str:
    """Takes a string and adds an additional line to the CP2K input file if the SCAN or R2SCAN functional is used

    Parameters
    ----------
    llist : str
        string to be modified
    """

    # if SCAN is used, add an addtional line to the CP2K input file
    # in the &XC_FUNCTIONAL section, add the line: PARAMETRIZATION SCAN
    if "SCAN" in llist:
        llist = re.sub(
            "&XC_FUNCTIONAL SCAN",
            "&XC_FUNCTIONAL\n\t\t\t\t&MGGA_C_SCAN\n\t\t\t\t&END MGGA_C_SCAN\n\t\t\t\t&MGGA_X_SCAN\n\t\t\t\t&END MGGA_X_SCAN",
            llist,
        )
    elif "R2SCAN" in llist:
        llist = re.sub(
            "&XC_FUNCTIONAL R2SCAN",
            "&XC_FUNCTIONAL\n\t\t\t\t&MGGA_C_R2SCAN\n\t\t\t\t&END MGGA_C_R2SCAN\n\t\t\t\t&MGGA_X_R2SCAN\n\t\t\t\t&END MGGA_X_R2SCAN",
            llist,
        )

    return llist


# Modify the CP2K input files for the AIMD simulation
def adjust_cp2k_input_aimd(
    cp2k_infiles: list[str], which_jobs: list[bool], data: dict[str, Any]
) -> None:
    """Adjust the CP2K input files for an AIMD simulation

    Parameters
    ----------
    cp2k_infiles : list
        List of the CP2K input files as strings
    which_jobs : list
        List of booleans indicating which jobs are to be executed
    data : dict
        Dictionary with the data from the command line arguments, including default values
    """

    # check if this function was called for the correct type of calculation
    if data["type"] != "aimd":
        sys.exit(
            "Error: adjust_cp2k_input_aimd() was called for the wrong type of calculation."
        )

    for i, file in enumerate(cp2k_infiles):
        # open the file
        with open(file, "r") as f:
            # the file is read into a list of lines, the string is changed and the file is written again
            lines = []
            lines = f.read()
            lines = re.sub(
                "Part of the AIMD setup tool", "Created by the AIMD setup tool", lines
            )

            # for the geometry optimization: adjust project name, box length, coord file, density functional, basis set, pseudopotential
            if i == 0 and which_jobs[i] == True:
                lines = re.sub("\$\{PROJECT_NAME\}", str(data["project"]), lines)
                lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
                lines = re.sub("\$\{SIMBOX_XYZ\}", str(data["coord"]), lines)
                lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
                lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
                lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)
                if data["func"] == "REVPBE":
                    lines = revpbe_adjustment(lines)
                elif data["func"] == "SCAN" or data["func"] == "R2SCAN":
                    lines = scan_adjustment(lines)
                lines = remove_comments_and_whitespace(lines)

                with open(file, "w") as g:
                    g.writelines(lines)

            # for the equilibration: adjust project name, box length, coord file, thermostat, temperature and number of steps, density functional, basis set, pseudopotential
            elif i == 1 and which_jobs[i] == True:
                lines = re.sub("\$\{PROJECT_NAME\}", str(data["project"]), lines)
                lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
                lines = re.sub("\$\{SIMBOX_XYZ\}", str(data["coord"]), lines)
                lines = re.sub("\$\{THERMO\}", str(data["thermo"]), lines)
                lines = re.sub("\$\{TEMP\}", str(data["t_equi"]), lines)
                lines = re.sub("\$\{NSTEPS\}", str(data["steps_equi"]), lines)
                lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
                lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
                lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)
                if data["func"] == "REVPBE":
                    lines = revpbe_adjustment(lines)
                elif data["func"] == "SCAN" or data["func"] == "R2SCAN":
                    lines = scan_adjustment(lines)

                # if a velocity file is provided, add the velocities to the input file
                if data["velocity"] is not None:
                    # insert the velocity section after the topology section
                    with open(data["velocity"], "r") as h:
                        velocity_lines = h.read()
                        lines = re.sub(
                            "&END TOPOLOGY",
                            "&END TOPOLOGY\n\t\t"
                            + "&VELOCITY\n"
                            + velocity_lines
                            + "\t\t"
                            + "&END VELOCITY\n\t",
                            lines,
                        )
                    # remove the restart section from the input file
                    # remove the last three lines of the input file
                    lines = re.sub("\n&EXT_RESTART\n.*\n&END EXT_RESTART", "", lines)

                lines = remove_comments_and_whitespace(lines)

                with open(file, "w") as g:
                    g.writelines(lines)

            # for the relaxation: adjust project name, box length, coord file, thermostat, temperature and number of steps, density functional, basis set, pseudopotential
            elif i == 2 and which_jobs[i] == True:
                lines = re.sub("\$\{PROJECT_NAME\}", str(data["project"]), lines)
                lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
                lines = re.sub("\$\{SIMBOX_XYZ\}", str(data["coord"]), lines)
                lines = re.sub("\$\{THERMO\}", str(data["thermo"]), lines)
                lines = re.sub("\$\{TEMP\}", str(data["t_relax"]), lines)
                lines = re.sub("\$\{NSTEPS\}", str(data["steps_relax"]), lines)
                lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
                lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
                lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)
                if data["func"] == "REVPBE":
                    lines = revpbe_adjustment(lines)
                elif data["func"] == "SCAN" or data["func"] == "R2SCAN":
                    lines = scan_adjustment(lines)
                lines = remove_comments_and_whitespace(lines)

                with open(file, "w") as g:
                    g.writelines(lines)

            # for the production: adjust project name, box length, coord file, thermostat, temperature and number of steps, density functional, basis set, pseudopotential, ensemble and Wannier if desired
            elif i == 3 and which_jobs[i] == True:
                lines = re.sub("\$\{PROJECT_NAME\}", str(data["project"]), lines)
                lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
                lines = re.sub("\$\{SIMBOX_XYZ\}", str(data["coord"]), lines)
                lines = re.sub("\$\{THERMO\}", str(data["thermo"]), lines)
                lines = re.sub("\$\{TEMP\}", str(data["t_prod"]), lines)
                lines = re.sub("\$\{NSTEPS\}", str(data["steps_prod"]), lines)
                lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
                lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
                lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)
                lines = re.sub("\$\{ENSEMBLE\}", str(data["ensemble"]), lines)

                if data["func"] == "REVPBE":
                    lines = revpbe_adjustment(lines)
                elif data["func"] == "SCAN" or data["func"] == "R2SCAN":
                    lines = scan_adjustment(lines)
                lines = remove_comments_and_whitespace(lines)

                with open(file, "w") as g:
                    g.writelines(lines)

                # if NVE ensemble is used, remove the thermostat
                if data["ensemble"] == "NVE":
                    with open(file, "r+") as f:
                        f.seek(0)
                        lines = []
                        lines = f.readlines()
                        for j, line in enumerate(lines):
                            if "&THERMOSTAT" in line:
                                # print("found thermostat")
                                lines[j - 1] = ""
                                for k in range(j, len(lines)):
                                    if "&END THERMOSTAT" in lines[k]:
                                        lines[k] = ""
                                        break
                                    else:
                                        lines[k] = ""
                    with open(file, "w") as g:
                        g.writelines(lines)

                # if wannier is not requested, remove the section from the input file
                if data["wannier"] == False:
                    with open(file, "r+") as f:
                        # set the pointer to the beginning of the file
                        f.seek(0)
                        lines = []
                        lines = f.readlines()

                        for j, line in enumerate(lines):
                            # find start of wannier section
                            if "&LOCALIZE" in line:
                                lines[j] = ""
                                for k in range(j, len(lines)):
                                    if "&END LOCALIZE" in lines[k]:
                                        lines[k] = ""
                                        break
                                    else:
                                        lines[k] = ""
                    with open(file, "w") as g:
                        g.writelines(lines)

                # if BQB printing is not requested, remove the section from the input file
                if data["bqb_in_prod"] == False:
                    with open(file, "r+") as f:
                        # set the pointer to the beginning of the file
                        f.seek(0)
                        lines = []
                        lines = f.readlines()

                        for j, line in enumerate(lines):
                            # find start of wannier section
                            if "&E_DENSITY_BQB" in line:
                                lines[j - 1] = ""
                                lines[j] = ""
                                for k in range(j, len(lines)):
                                    if "&END PRINT" in lines[k]:
                                        lines[k] = ""
                                        break
                                    else:
                                        lines[k] = ""
                    with open(file, "w") as g:
                        g.writelines(lines)


# modify the CP2K input file for a single point calculation
def adjust_cp2k_input_sp(cp2k_infiles: list[str], data: dict[str, Any]) -> None:
    """Adjust the CP2K input file for a single point calculation

    Parameters
    ----------
    cp2k_infiles : str
        filename of the CP2K input file
    data : dict
        dictionary containing the data for the calculation
    """

    # check if this function was called for the correct type of calculation
    if data["type"] != "energy":
        sys.exit(
            "Error: adjust_cp2k_input_sp() was called for the wrong type of calculation."
        )

    for i, file in enumerate(cp2k_infiles):
        with open(file, "r") as f:
            # the file is read into a list of lines, the string is changed and the file is written again
            lines = []
            lines = f.read()
            lines = re.sub(
                "Part of the AIMD setup tool", "Created by the AIMD setup tool", lines
            )
            lines = re.sub("\$\{PROJECT_NAME\}", str(data["project"]), lines)
            lines = re.sub("\$\{SIMBOX_XYZ\}", str(data["coord"]), lines)
            lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
            lines = re.sub("\$\{COORD_FILE\}", str(data["coord"]), lines)
            lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
            lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
            lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)

            if data["func"] == "REVPBE":
                lines = revpbe_adjustment(lines)
            elif data["func"] == "SCAN" or data["func"] == "R2SCAN":
                lines = scan_adjustment(lines)
            lines = remove_comments_and_whitespace(lines)

            with open(file, "w") as g:
                g.writelines(lines)


# modify the CP2K input file for the bqb calculations
def adjust_cp2k_input_bqb(
    cp2k_infiles: list[str],
    data: dict[str, Any],
    runscript_name: str,
    queue: str,
    template_dir: str,
) -> None:
    """Adjust the CP2K input file for the bqb file production

    Parameters
    ----------
    cp2k_infiles : str
        filename of the CP2K input file
    data : dict
        dictionary containing the data for the calculation
    project : str
        name of the project
    runscript_name : str
        name of the runscript
    queue : str
        name of the queue to submit the job to
    template_dir : str
        path to the directory containing the template files
    """

    # check if this function was called for the correct type of calculation
    if data["type"] != "bqb":
        sys.exit(
            "Error: adjust_cp2k_input_bqb() was called for the wrong type of calculation."
        )

    # determine important parameters according to type of spectrum
    # taken from: https://brehm-research.de/files/spec_tutorial_2018.pdf
    if data["spectrum"] == "ir":
        calc_efield = False
        stride = 8
        overlap = 0
    elif data["spectrum"] == "raman":
        calc_efield = True
        stride = 8
        overlap = 0
    elif data["spectrum"] == "vcd":
        calc_efield = False
        stride = 1
        overlap = 2
    elif data["spectrum"] == "roa":
        calc_efield = True
        stride = 1
        overlap = 2
    elif data["spectrum"] == "dipoles":
        calc_efield = False
        stride = 1
        overlap = 0
    else:
        sys.exit("Error: Invalid spectrum type.")

    for i, file in enumerate(cp2k_infiles):
        with open(file, "r") as f:
            if i == 0:
                # the file is read into a list of lines, the string is changed and the file is written again
                lines = []
                lines = f.read()

                lines = re.sub(
                    "Part of the AIMD setup tool",
                    "Created by the AIMD setup tool",
                    lines,
                )
                lines = re.sub("\$\{PROJECT_NAME\}", str(data["project"]), lines)
                lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
                lines = re.sub("\$\{SIMBOX_XYZ\}", str(data["coord"]), lines)
                lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
                lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
                lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)
                lines = re.sub("\$\{NSTEPS\}", str(data["steps_bqb"] + overlap), lines)
                lines = re.sub("\$\{STRIDE\}", str(stride), lines)
                lines = re.sub(
                    "\$\{TRAJ_FILE_NAME\}",
                    str(os.path.basename(data["reftraj"])),
                    lines,
                )
                if data["func"] == "REVPBE":
                    lines = revpbe_adjustment(lines)
                elif data["func"] == "SCAN" or data["func"] == "R2SCAN":
                    lines = scan_adjustment(lines)
                lines = remove_comments_and_whitespace(lines)

                with open(file, "w") as g:
                    g.writelines(lines)

                # generate n_bqb directories for the bqb calculations
                # if no e field is needed, one directory per bqb is enough
                if calc_efield == False:
                    # create the directories
                    for j in range(data["n_bqb"]):
                        os.mkdir("bqb_" + str(j + 1).zfill(2))

                        # change into the directory
                        os.chdir("bqb_" + str(j + 1).zfill(2))

                        # copy the bqb input file
                        os.system("cp ../bqb.inp .")

                        # adjust the bqb input file
                        # first / last snapshot and field direction
                        with open("bqb.inp", "r") as h:
                            first_step = (
                                data["start_from"] + j * data["steps_bqb"] * stride
                            )
                            last_step = (
                                data["start_from"]
                                + j * data["steps_bqb"] * stride
                                + data["steps_bqb"] * stride
                                + overlap
                                - 1 * stride
                            )

                            lines = []
                            lines = h.read()
                            lines = re.sub(
                                "\$\{FIRST_SNAPSHOT\}", str(first_step), lines
                            )
                            lines = re.sub("\$\{LAST_SNAPSHOT\}", str(last_step), lines)
                            lines = re.sub("\$\{FIELD_DIRECTION\}", str("no"), lines)

                            # write the adjusted bqb input file
                            with open("bqb.inp", "w") as k:
                                k.writelines(lines)

                            # copy the cp2k data files and runscript to the bqb directories
                            copy_cp2k_data_and_runscript(
                                template_dir=template_dir,
                                project_dir=".",
                                runscript=runscript_name,
                            )
                            # adjust the runscript
                            adjust_runscript(
                                runscript=runscript_name,
                                project="bqb_" + str(j + 1).zfill(2),
                                queue=queue,
                            )

                        # change back to the main directory
                        os.chdir("..")

                    # remove the bqb input file from the main directory
                    os.system("rm bqb.inp")

                # if an e field is needed, three additional directories are needed
                elif calc_efield == True:
                    # iterate over the number of bqb files
                    for j in range(data["n_bqb"]):
                        # create the directories
                        os.mkdir("bqb_" + str(j + 1).zfill(2) + "_no-field")
                        os.mkdir("bqb_" + str(j + 1).zfill(2) + "_x-field")
                        os.mkdir("bqb_" + str(j + 1).zfill(2) + "_y-field")
                        os.mkdir("bqb_" + str(j + 1).zfill(2) + "_z-field")

                        # iterate over the four above directories
                        for k in range(4):
                            # change into the directory
                            if k == 0:
                                os.chdir("bqb_" + str(j + 1).zfill(2) + "_no-field")
                            elif k == 1:
                                os.chdir("bqb_" + str(j + 1).zfill(2) + "_x-field")
                            elif k == 2:
                                os.chdir("bqb_" + str(j + 1).zfill(2) + "_y-field")
                            elif k == 3:
                                os.chdir("bqb_" + str(j + 1).zfill(2) + "_z-field")

                            # copy the bqb input file
                            os.system("cp ../bqb.inp .")

                            # adjust the bqb input file
                            # first / last snapshot and field direction
                            with open("bqb.inp", "r") as h:
                                # define the first and last snapshot
                                first_step = (
                                    data["start_from"] + j * data["steps_bqb"] * stride
                                )
                                last_step = (
                                    data["start_from"]
                                    + j * data["steps_bqb"] * stride
                                    + data["steps_bqb"] * stride
                                    + overlap
                                    - 1 * stride
                                )

                                lines = []
                                lines = h.read()
                                lines = re.sub(
                                    "\$\{FIRST_SNAPSHOT\}", str(first_step), lines
                                )
                                lines = re.sub(
                                    "\$\{LAST_SNAPSHOT\}", str(last_step), lines
                                )

                                # substitute the field direction, and the polarization vector
                                if k == 0:
                                    lines = re.sub(
                                        "\$\{FIELD_DIRECTION\}", str("no"), lines
                                    )
                                    lines = re.sub(
                                        "\$\{X_POL\} \$\{Y_POL\} \$\{Z_POL\}",
                                        str("0.0 0.0 0.0"),
                                        lines,
                                    )
                                elif k == 1:
                                    lines = re.sub(
                                        "\$\{FIELD_DIRECTION\}", str("x"), lines
                                    )
                                    lines = re.sub(
                                        "\$\{X_POL\} \$\{Y_POL\} \$\{Z_POL\}",
                                        str("1.0 0.0 0.0"),
                                        lines,
                                    )
                                elif k == 2:
                                    lines = re.sub(
                                        "\$\{FIELD_DIRECTION\}", str("y"), lines
                                    )
                                    lines = re.sub(
                                        "\$\{X_POL\} \$\{Y_POL\} \$\{Z_POL\}",
                                        str("0.0 1.0 0.0"),
                                        lines,
                                    )
                                elif k == 3:
                                    lines = re.sub(
                                        "\$\{FIELD_DIRECTION\}", str("z"), lines
                                    )
                                    lines = re.sub(
                                        "\$\{X_POL\} \$\{Y_POL\} \$\{Z_POL\}",
                                        str("0.0 0.0 1.0"),
                                        lines,
                                    )

                                # write the adjusted bqb input file
                                with open("bqb.inp", "w") as s:
                                    s.writelines(lines)

                                # remove comment symbols (#) from the periodic efield block if the direction is not "no"
                                if k != 0:
                                    # set the pointer to the beginning of the file
                                    h.seek(0)
                                    lines = h.readlines()
                                    for m, line in enumerate(lines):
                                        # find start of section
                                        if "&PERIODIC_EFIELD" in line:
                                            # remove comment symbols from the following lines until the end of the section
                                            for n in range(m, len(lines)):
                                                if "&END PERIODIC_EFIELD" in lines[n]:
                                                    lines[n] = lines[n][1:]
                                                    break
                                                # remove first comment symbol
                                                else:
                                                    lines[n] = lines[n][1:]

                                # write the adjusted bqb input file
                                with open("bqb.inp", "w") as s:
                                    s.writelines(lines)

                                # copy the cp2k data files and runscript to the bqb directories
                                copy_cp2k_data_and_runscript(
                                    template_dir=template_dir,
                                    project_dir=".",
                                    runscript=runscript_name,
                                )
                                # adjust the runscript
                                adjust_runscript(
                                    runscript=runscript_name,
                                    project=str(os.path.basename(os.getcwd())),
                                    queue=queue,
                                )

                            # change back to the main directory
                            os.chdir("..")

                    # remove the bqb input file from the main directory
                    os.system("rm bqb.inp")


# modify the bash runscript for the queue system
def adjust_runscript(
    runscript: str, project: str, queue: str, ncpu: int, joblist: list[bool]
) -> None:
    """Adjust the runscript for the queue system

    Parameters
    ----------
    runscript : str
        filename of the runscript
    project : str
        project name
    queue : str
        queue system to execute the calculation
    ncpu : int
        number of CPUs to use
    joblist : list
        list of booleans indicating which jobs are to be executed
    """

    # open the file
    with open(runscript, "r") as f:
        # the file is read into a list of lines, the string is changed and the file is written again
        lines = []
        lines = f.read()
        lines = re.sub("PROJECT_NAME", project, lines)
        lines = re.sub("QUEUE_NAME", queue, lines)
        lines = re.sub(
            "Part of the AIMD setup tool",
            "Created by the AIMD setup tool",
            lines,
        )
        lines = re.sub("N_CPU", str(ncpu), lines)

        jobs = ["geoopt", "eq", "relax", "prod"]

        for i, job in enumerate(jobs):
            if joblist[i] == False:
                lines = re.sub(".*" + job + ".*\n", "", lines)

        # remove the job submission lines for jobs that are not requested

        with open(runscript, "w") as g:
            g.writelines(lines)
