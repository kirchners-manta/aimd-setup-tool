#!/usr/bin/python3

# Part of the AIMD setup tool
# Written by Tom Frömbgen
# Last modified 2023-01-23

import re

# Modify the CP2K input files
def adjust_cp2k_input(cp2k_infiles: list, data: dict) -> None:
    """Adjust the CP2K input files.

    Parameters
    ----------
    cp2k_infiles : list
        List of the CP2K input files as PosixPath objects.
    data : dict
        Dictionary with the data from the command line arguments, including default values.
    """
    
    for i, file in enumerate(cp2k_infiles):

        # open the file
        with open(file, "r") as f:
            # the file is read into a list of lines, the string is changed and the file is written again
            lines = []
            lines = f.read()

            # for the geometry optimization: adjust project name, box length, coord file, density functional, basis set, pseudopotential
            if i == 0:
                
                lines = re.sub("\$\{PROJECT_NAME\}", str(data["project"]), lines)
                lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
                lines = re.sub("\$\{SIMBOX_XYZ\}", str(data["coord"]), lines)
                lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
                lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
                lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)

                with open(file, "w") as g:
                    g.writelines(lines)


            # for the equilibration: adjust project name, box length, coord file, thermostat, temperature and number of steps, density functional, basis set, pseudopotential
            elif i == 1:
                 
                lines = re.sub("\$\{PROJECT_NAME\}", str(data["project"]), lines)
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
                
                lines = re.sub("\$\{PROJECT_NAME\}", str(data["project"]), lines)
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
  
                lines = re.sub("\$\{PROJECT_NAME\}", str(data["project"]), lines)
                lines = re.sub("\$\{BOX_LENGTH\}", str(data["boxsize"]), lines)
                lines = re.sub("\$\{SIMBOX_XYZ\}", str(data["coord"]), lines)
                lines = re.sub("\$\{THERMO\}", str(data["thermo"]), lines)
                lines = re.sub("\$\{TEMP\}", str(data["t_prod"]), lines)
                lines = re.sub("\$\{NSTEPS\}", str(data["steps_prod"]), lines)
                lines = re.sub("\$\{FUNC\}", str(data["func"]), lines)
                lines = re.sub("\$\{BASIS\}", str(data["basis"]), lines)
                lines = re.sub("\$\{PP_FUNC\}", str(data["pp_func"]), lines)
                
                # if wannier is requested, adjust the input file
                # remove the comment symbols (#) from the wannier section
                if data["wannier"] == True:
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


# adjust the cluster submission script
def adjust_runscript(runscript: str, project: str) -> None:
    
    # open the file
    with open(runscript, "r") as f:
        
        # the file is read into a list of lines, the string is changed and the file is written again
        lines = []
        lines = f.read()
        lines = re.sub("PROJECT_NAME", project, lines)
        
        with open(runscript, "w") as g:
            g.writelines(lines)