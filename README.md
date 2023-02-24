# AIMD template
---
*This project is still under development. 
Regularly updating your repo and reading this document is recommended.*

Python3 script and collection of input files to set up single point calculations, AIMD simulations or bqb file productions in CP2K.

I recommend adding the script `aimd-setup.py` to your path, e.g. by creating a symlink to your bin. 

```bash
ln -s ABSOLUTE_PATH_TO_THIS_DIR/aimd-setup.py ~/bin/aimd-setup
```

Doing so, you can call the program from anywhere. 
Calling it with the `-h` option will print a help message with all the options.
    
```bash
aimd-setup -h
```
There is one required argument, the project name (using the `-p` flag). 
This is the name of the directory in which all the files will be stored. 

```bash
aimd-setup -p PROJECT_NAME
``` 
If the directory already exists, the program will ask you if you want to overwrite it.
Then, you can specify which type of calculation you want to set up with the `-t` flag.
The options are:
* `single-point`
* `aimd` (default)
* `bqb` (under development)

There are more options to specify the calculation, e.g. energy cutoff, the number of steps, the time step, the temperature, etc.
All of these options have default values. 
Once you call the program and set up a calculation, the chosen options (including the default ones) will be printed to the screen.

