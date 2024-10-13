# -*- coding: utf-8 -*-
#
# Copyright (c) 2024 BerniK86.
#
# This file is part of pyprojectboard
# (see https://github.com/bernik86/pyprojectboard).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

# pylint: disable=missing-docstring

import json
import os
from pathlib import Path
from typing import Any

# pylint: disable=import-error
from data import defaults  # type: ignore

# pylint: enable=import-error


__SETTINGS_FILE__ = os.path.expanduser(defaults.SETTINGS_FILE)
__settings__ = {}


def __set_default_settings__():
    __settings__["boards"] = []
    __settings__["window_width"] = 1200
    __settings__["window_height"] = 800
    __settings__["data_dir"] = os.path.expanduser(defaults.DATA_DIR)
    __settings__["default_states"] = defaults.DEFAULT_STATES


def reset_to_default_settings():
    __set_default_settings__()


def get_settings_copy() -> dict:
    return dict(__settings__)


def get_setting(key: str) -> Any:
    assert key in __settings__
    return __settings__[key]


def set_setting(key: str, value: Any):
    __settings__[key] = value


def append_to_setting(key: str, value: Any):
    assert isinstance(__settings__[key], list)

    if isinstance(value, list):
        __settings__[key].extend(value)
    else:
        __settings__[key].append(value)


def print_settings():
    print(__settings__)


def load_settings():
    __set_default_settings__()
    filename = os.path.expanduser(__SETTINGS_FILE__)

    if not os.path.isfile(filename):
        settings_file = Path(filename)
        settings_file.parent.mkdir(exist_ok=True, parents=True)
        save_settings()
        return

    with open(filename, "rt", encoding="UTF-8") as settings_file:
        json_str = "\n".join(settings_file.readlines())

    decoder = json.JSONDecoder()
    json_dict = decoder.decode(json_str)
    __settings__.update(json_dict)


def save_settings():
    encoder = json.JSONEncoder()
    json_str = encoder.encode(__settings__)
    filename = os.path.expanduser(__SETTINGS_FILE__)
    with open(filename, "wt", encoding="UTF-8") as settings_file:
        settings_file.write(json_str)
