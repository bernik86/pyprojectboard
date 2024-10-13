<!--
Copyright (c) 2022 bernik86.

This file is part of pyprojectboard 
(see https://github.com/bernik86/pyprojectboard).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
-->
# pyprojectboard
Simple personal project management tool. It is based on the classical waterfall project management method.

## Installation

### Installation script

An installation script can be found in the `scripts` folder. 
This script creates a virtual python environment for the program, installs all the python dependencies, and creates and links a script for executing `pyprojectboard`.
The script for executing `pyprojectboard` is linked to `$HOME/.local/bin`.
The installation script has only been tested on Debian 12.7. 
However, in principle, the script should also work on other Linux distribution.


#### Non-pip dependencies

`pyprojectboard` requires the following packages to be installed globally (names from Debian 12.7):

-	python3.11-venv 
-	libxcb-cursor-dev


Furthermore, some version of the Qt framework need to be installed. 
On Debian 12.7 with XFce desktop, all necessary Qt libraries are already installed and the two libraries listed above are installed by the installation script.

The installation script will be tested on more distributions and the installation instructions added here as development progresses. 


## Running pyprojectboard

### On Debian 12.7

The installation script generates a script to run `pyprojectboard` in the `bin` sub-folder in the root directory of the git repository.
The script is linked to `$HOME/.local/bin`.
If `$HOME/.local/bin` is in the `PATH` variable (check using: `echo $PATH`), the program can be run typing the following command in a terminal:

`pyprojectboard`



## Contributing

If you would like to contribute, you can create a pull request or drop me an email to: berni86@duck.com 


## TODO

### General

- [ ] Test installation on more distributions
- [ ] Write user manual

### Features

- [ ] Export function
- [ ] Project plan
- [ ] Project schedule

