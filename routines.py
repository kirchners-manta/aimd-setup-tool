#!/usr/bin/python3

# Part of the AIMD setup tool
# Written by Tom Frömbgen
# Last modified 2023-01-23

import sys
import re
import os

#############################################

# Copy the CP2K data files and the runscript to a directory


def copy_cp2k_data_and_runscript(template_dir: str, project_dir: str, runscript: str) -> None:
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
    os.system("cp " + template_dir + "/data/* " + project_dir)

    # copy the runscript
    os.system("cp " + template_dir + "/execute/" +
              runscript + " " + project_dir)

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

                with open(file, "w") as g:
                    g.writelines(lines)

            # for the relaxation: adjust project name, box length, coord file, thermostat, temperature and number of steps, density functional, basis set, pseudopotential
            elif i == 2:

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

                with open(file, "w") as g:
                    g.writelines(lines)

                # if wannier is requested, adjust the input file
                # remove the comment symbols (#) from the wannier section
                if data["wannier"] == True:
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

            with open(file, "w") as g:
                g.writelines(lines)

# modify the CP2K input file for the bqb calculations


def adjust_cp2k_input_bqb(cp2k_infiles: list, data: dict, project: str, runscript_name: str, queue: str, template_dir: str) -> None:
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
            "Error: adjust_cp2k_input_bqb() was called for the wrong type of calculation.")

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

    for i, file in enumerate(cp2k_infiles):

        with open(file, "r") as f:

            if i == 0:

                # the file is read into a list of lines, the string is changed and the file is written again
                lines = []
                lines = f.read()
                lines = re.sub("\$\{PROJECT_NAME\}",
                               str(data["project"]), lines)
                lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
                lines = re.sub("\$\{SIMBOX_XYZ\}", str(data["coord"]), lines)
                lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
                lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
                lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)
                lines = re.sub("\$\{NSTEPS\}", str(
                    data["steps_bqb"] + overlap), lines)
                lines = re.sub("\$\{STRIDE\}", str(stride), lines)
                lines = re.sub("\$\{TRAJ_FILE_NAME\}", str(
                    os.path.basename(data["reftraj"])), lines)

                with open(file, "w") as g:
                    g.writelines(lines)

                # generate n_bqb directories for the bqb calculations
                # if no e field is needed, one directory per bqb is enough
                if calc_efield == False:

                    # create the directories
                    for j in range(data["n_bqb"]):

                        os.mkdir("bqb_" + str(j + 1))

                        # change into the directory
                        os.chdir("bqb_" + str(j + 1))

                        # copy the bqb input file
                        os.system("cp ../bqb.inp .")

                        # adjust the bqb input file
                        # first / last snapshot and field direction
                        with open("bqb.inp", "r") as h:

                            first_step = data["start_from"] + \
                                j * data["steps_bqb"] * stride
                            last_step = data["start_from"] + j * \
                                data["steps_bqb"] * stride + \
                                data["steps_bqb"] * stride + \
                                overlap - 1 * stride

                            lines = []
                            lines = h.read()
                            lines = re.sub("\$\{FIRST_SNAPSHOT\}",
                                           str(first_step), lines)
                            lines = re.sub("\$\{LAST_SNAPSHOT\}",
                                           str(last_step), lines)
                            lines = re.sub(
                                "\$\{FIELD_DIRECTION\}", str("no"), lines)

                            # write the adjusted bqb input file
                            with open("bqb.inp", "w") as k:
                                k.writelines(lines)

                            # copy the cp2k data files and runscript to the bqb directories
                            copy_cp2k_data_and_runscript(template_dir=template_dir,
                                                         project_dir=".",
                                                         runscript=runscript_name)
                            # adjust the runscript
                            adjust_runscript(runscript=runscript_name,
                                             project="bqb_" + str(j + 1),
                                             queue=queue,)

                        # change back to the main directory
                        os.chdir("..")

                    # remove the bqb input file from the main directory
                    os.system("rm bqb.inp")

                # if an e field is needed, three additional directories are needed
                elif calc_efield == True:

                    # iterate over the number of bqb files
                    for j in range(data["n_bqb"]):

                        # create the directories
                        os.mkdir("bqb_" + str(j + 1) + "_no-field")
                        os.mkdir("bqb_" + str(j + 1) + "_x-field")
                        os.mkdir("bqb_" + str(j + 1) + "_y-field")
                        os.mkdir("bqb_" + str(j + 1) + "_z-field")

                        # iterate over the four above directories
                        for k in range(4):

                            # change into the directory
                            if k == 0:
                                os.chdir("bqb_" + str(j + 1) + "_no-field")
                            elif k == 1:
                                os.chdir("bqb_" + str(j + 1) + "_x-field")
                            elif k == 2:
                                os.chdir("bqb_" + str(j + 1) + "_y-field")
                            elif k == 3:
                                os.chdir("bqb_" + str(j + 1) + "_z-field")

                            # copy the bqb input file
                            os.system("cp ../bqb.inp .")

                            # adjust the bqb input file
                            # first / last snapshot and field direction
                            with open("bqb.inp", "r") as h:

                                # define the first and last snapshot
                                first_step = data["start_from"] + \
                                    j * data["steps_bqb"] * stride
                                last_step = data["start_from"] + j * \
                                    data["steps_bqb"] * stride + \
                                    data["steps_bqb"] * stride + \
                                    overlap - 1 * stride

                                lines = []
                                lines = h.read()
                                lines = re.sub("\$\{FIRST_SNAPSHOT\}",
                                               str(first_step), lines)
                                lines = re.sub("\$\{LAST_SNAPSHOT\}",
                                               str(last_step), lines)

                                # substitute the field direction, and the polarization vector
                                if k == 0:
                                    lines = re.sub(
                                        "\$\{FIELD_DIRECTION\}", str("no"), lines)
                                    lines = re.sub("\$\{X_POL\} \$\{Y_POL\} \$\{Z_POL\}", str(
                                        "0.0 0.0 0.0"), lines)
                                elif k == 1:
                                    lines = re.sub(
                                        "\$\{FIELD_DIRECTION\}", str("x"), lines)
                                    lines = re.sub("\$\{X_POL\} \$\{Y_POL\} \$\{Z_POL\}", str(
                                        "1.0 0.0 0.0"), lines)
                                elif k == 2:
                                    lines = re.sub(
                                        "\$\{FIELD_DIRECTION\}", str("y"), lines)
                                    lines = re.sub("\$\{X_POL\} \$\{Y_POL\} \$\{Z_POL\}", str(
                                        "0.0 1.0 0.0"), lines)
                                elif k == 3:
                                    lines = re.sub(
                                        "\$\{FIELD_DIRECTION\}", str("z"), lines)
                                    lines = re.sub("\$\{X_POL\} \$\{Y_POL\} \$\{Z_POL\}", str(
                                        "0.0 0.0 1.0"), lines)

                                # write the adjusted bqb input file
                                with open("bqb.inp", "w") as s:
                                    s.writelines(lines)

                                # remove comment symbols (#) from the periodic efield block if the direction is not "no"
                                if k != 0:
                                    print(k)
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
                                copy_cp2k_data_and_runscript(template_dir=template_dir,
                                                             project_dir=".",
                                                             runscript=runscript_name)
                                # adjust the runscript
                                adjust_runscript(runscript=runscript_name,
                                                 project=str(os.path.basename(os.getcwd())), queue=queue,)

                                # change back to the main directory
                                os.chdir("..")


# modify the bash runscript for the queue system


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
