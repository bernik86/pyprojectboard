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

import unittest

# pylint: disable=import-error
from data.settings import __set_default_settings__  # type: ignore
from data.settings import append_to_setting
from data.settings import get_setting
from data.settings import get_settings_copy
from data.settings import load_settings
from data.settings import reset_to_default_settings
from data.settings import save_settings
from data.settings import set_setting

# pylint: enable=import-error


class TestSettings(unittest.TestCase):

    def setUp(self):
        __set_default_settings__()

    def test_1_default_settings(self):
        settings = get_settings_copy()

        self.assertEqual([], settings["boards"])
        self.assertEqual(1200, settings["window_width"])
        self.assertEqual(800, settings["window_height"])

    def test_2_set_setting(self):
        set_setting("window_width", 2000)
        set_setting("version", "0.01 ALPHA")

        settings = get_settings_copy()
        self.assertEqual(2000, settings["window_width"])
        self.assertEqual("0.01 ALPHA", settings["version"])

    def test_3_reset_default_settings(self):
        set_setting("window_width", 2000)
        reset_to_default_settings()

        settings = get_settings_copy()
        self.assertEqual(1200, settings["window_width"])

    def test_4_get_setting(self):
        set_setting("geometry", (2000, 1000))
        set_setting("version", "0.01 ALPHA")

        with self.assertRaises(AssertionError):
            _ = get_setting("open tabs")

        version = get_setting("version")
        self.assertEqual("0.01 ALPHA", version)

    def test_5_append_to_list_setting(self):
        append_to_setting("boards", "PB1")
        append_to_setting("boards", "PB2")
        boards = get_setting("boards")
        self.assertEqual(["PB1", "PB2"], boards)

        append_to_setting("boards", ["PB3", "PB4"])
        self.assertEqual(["PB1", "PB2", "PB3", "PB4"], boards)

        with self.assertRaises(AssertionError):
            append_to_setting("geometry", 1200)

    @unittest.skip("Skipped to prevent excessive amount of write operations on SSD")
    def test_6_save_reset_load(self):
        set_setting("window_width", 2000)
        set_setting("window_height", 1000)
        set_setting("version", "0.01 ALPHA")
        append_to_setting("boards", "PB1")
        append_to_setting("boards", "PB2")

        save_settings()
        reset_to_default_settings()
        load_settings()

        boards = get_setting("boards")
        self.assertEqual(["PB1", "PB2"], boards)

        version = get_setting("version")
        self.assertEqual("0.01 ALPHA", version)

        geometry = (get_setting("window_width"), get_setting("window_height"))
        self.assertEqual((2000, 1000), geometry)
