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

import os
import unittest

# pylint: disable=import-error
from gui.qt.main_window import convert_str_to_filename  # type: ignore

# pylint: enable=import-error


class TestGUIHelperFunctions(unittest.TestCase):

    def test_1_convert_str_to_filename(self):
        names = ["test.json", "test123", "test @3", "test1-11.jsob"]
        clean_names = ["test.json", "test123.json", "test3.json", "test111.jsob.json"]
        directory = "~/Documents/pyprojectboards"
        directory = os.path.expanduser(directory)
        for name, clean_name in zip(names, clean_names):
            result = convert_str_to_filename(name)
            self.assertEqual(result, os.path.join(directory, clean_name))
