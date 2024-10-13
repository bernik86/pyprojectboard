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
from data import state  # type: ignore

# pylint: enable=import-error


class TestStateInt(unittest.TestCase):

    def test_1_init(self):
        state_1 = state.StateInt(1, [1, 2, 3], ["P", "M", "T"])
        self.assertEqual(state_1.__allowed__, [1, 2, 3])
        self.assertEqual(state_1.state, 1)
        self.assertEqual(state_1.__state__, [1])
        self.assertEqual(state_1.__state_names__, ["P", "M", "T"])

        state_1 = state.StateInt(1, [1, 2, 3])
        self.assertEqual(state_1.__state_names__, None)

        with self.assertRaises(ValueError):
            state_1 = state.StateInt(0, [1, 2, 3])

    def test_2_set_get(self):
        state_1 = state.StateInt(1, [1, 2, 3], ["P", "M", "T"])
        state_1.state = 2
        self.assertEqual(state_1.state, 2)
        self.assertEqual(state_1.prev_state, 1)

        state_1 = state.StateInt(1, [1, 2, 3], ["P", "M", "T"])
        self.assertEqual(state_1.state, 1)
        with self.assertRaises(ValueError):
            _ = state_1.prev_state

        with self.assertRaises(ValueError):
            state_1.state = "M"

        with self.assertRaises(ValueError):
            state_1.state = 100

    def test_3_add_sub(self):
        state_1 = state.StateInt(1, [1, 2, 3], ["P", "M", "T"])
        state_1 += 1

        self.assertEqual(state_1.state, 2)
        self.assertEqual(state_1.prev_state, 1)

        state_1 -= 1
        self.assertEqual(state_1.state, 1)
        self.assertEqual(state_1.prev_state, 2)

        with self.assertRaises(ValueError):
            state_1 += 100
        self.assertEqual(state_1.state, 1)
        self.assertEqual(state_1.prev_state, 2)

        with self.assertRaises(ValueError):
            state_1 -= 100
        self.assertEqual(state_1.state, 1)
        self.assertEqual(state_1.prev_state, 2)

    def test_4_comp_op(self):
        state_1 = state.StateInt(1, [1, 2, 3], ["P", "M", "T"])
        state_1 += 1

        self.assertTrue(state_1 == 2)
        self.assertTrue(state_1 < 3)
        self.assertTrue(state_1 > 1)
        self.assertTrue(state_1 >= 2)
        self.assertTrue(state_1 >= 1)
        self.assertTrue(state_1 <= 3)
        self.assertTrue(state_1 <= 2)

    def test_5_state_by_name(self):
        state_1 = state.StateInt(1, [1, 2, 3], ["P", "M", "T"])

        self.assertTrue(state_1.get_state_by_name("P"), 1)
        self.assertTrue(state_1.get_state_by_name("M"), 2)
        self.assertTrue(state_1.get_state_by_name("T"), 3)

        with self.assertRaises(ValueError):
            _ = state_1.get_state_by_name("K")

        state_1 = state.StateInt(1, [1, 2, 3])

        with self.assertRaises(ValueError):
            _ = state_1.get_state_by_name("P")

        setattr(state_1, "state", 3)
        self.assertEqual(state_1.state, 3)
