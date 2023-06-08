#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 bernik86.
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
from collections import OrderedDict
from typing import TypeVar

T = TypeVar("T")


class OrderableDict(OrderedDict):
    def __init__(self):
        self.order = []
        super().__init__(self)

    def __iter__(self):
        for key in self.order:
            yield key

    def __setitem__(self, key, value):
        if key not in self.order:
            self.order.append(key)
        super().__setitem__(key, value)

    def items(self):
        for key in self.order:
            yield key, super().__getitem__(key)

    def keys(self):
        # return self.__iter__()
        return iter(self)

    def values(self):
        for key in self.order:
            yield self[key]
            # yield super().__getitem__(key)

    def pop(self, key):
        item = super().pop(key)
        self.order.remove(key)
        return item

    def move(self, key: T, move_by: int = 1):
        idx = self.order.index(key)
        idx_new = idx + move_by
        self.order.insert(idx_new, self.order.pop(idx))
