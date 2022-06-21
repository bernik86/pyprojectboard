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
Simple personal project management tool.

## Dependencies

Apart from the python packages listed in `requirements.txt` (install via `pip install -r requirements.txt`), this program requires Qt6. The package to be installed is called `qt6-base` (at least on Debian and Manjaro). You can install it in the following way:

#### Debian

`sudo apt install qt6-base`

#### Manjaro

`sudo pacman -S qt6-base`

## Running pyprojectboard

### On Linux

Make the file `pyprojectboard.py` executable:

`chmod u+x pyprojectboard.py`

and then run:

`./pyprojectboard.py`

Note that so far I have only tested pyprojectboard on Debian and Manjaro Linux. Please report any issues you encounter on other platforms.

