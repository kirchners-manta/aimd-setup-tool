# AIMD template
---

Python script and collection of input files to set up AIMD simulations or bqb file productions in CP2K.
Python >=3.10 is required.

I recommend adding the script `aimd-setup.py` to your path, e.g. by creating a symlink to your bin. 

```bash
ln -s ABSOLUTE_PATH_TO_THIS_DIR/aimd-setup.py ~/bin/aimd-setup
```
If your local python version is not >=3.10, you can e.g. install conda and create a new environment with python 3.10. 
Then, you can add the path to the python executable to the first line of the script or you can add an alias to your `.bashrc` file.

```bash
alias aimd-setup='python3.10 ABSOLUTE_PATH_TO_THIS_DIR/aimd-setup.py'


Doing so, you can call the program from anywhere. 
Calling it with the `-h` option will print a help message with all the options.
    
```bash
aimd-setup -h
```
There is one required argument, the project name. 
This is the name of the directory in which all the files will be stored. 

```bash
aimd-setup [OPTIONS] project 
``` 
If the directory already exists, the program will ask you if you want to overwrite it.
Then, you can specify which type of calculation you want to set up with the `-t` flag.
The options are:
* `single-point` (under development)
* `aimd` (default)
* `bqb`

There are more options to specify the calculation, e.g. energy cutoff, the number of steps, the time step, the temperature, etc.
All of these options have default values. 
Once you call the program and set up a calculation, the chosen options (including the default ones) will be printed to the screen.

