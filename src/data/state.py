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

from typing import List
from typing import Optional
from typing import Self


class StateInt:
    def __init__(
        self, initial_state: int, allowed_states: List[int], state_names: Optional[List[str]] = None
    ):
        if initial_state not in allowed_states:
            raise ValueError("Initial state must be an allowed state!")
        self.__state__ = [initial_state]
        self.__allowed__ = list(allowed_states)

        self.__state_names__ = None
        if state_names is not None and len(allowed_states) == len(state_names):
            self.__state_names__ = state_names

    @property
    def state(self) -> int:
        return self.__state__[-1]

    @state.setter
    def state(self, new_state: int):
        if new_state not in self.__allowed__:
            raise ValueError(
                f"{new_state=} is not a valid state! Valid states: {self.__allowed__}!"
            )
        self.__state__.append(new_state)

    @property
    def prev_state(self) -> int:
        if len(self.__state__) < 2:
            raise ValueError("No previous state available!")
        return self.__state__[-2]

    def get_state_by_name(self, state_name: str) -> int:
        if self.__state_names__ is None:
            raise ValueError("No state names defined!")
        if state_name not in self.__state_names__:
            raise ValueError(f"{state_name=} is not a valid (valid states: {self.__state_names__})")
        idx = self.__state_names__.index(state_name)
        return self.__allowed__[idx]

    def get_current_state_name(self) -> str:
        if self.__state_names__ is None:
            raise ValueError
        idx = self.__allowed__.index(self.state)
        return self.__state_names__[idx]

    def __iadd__(self, other: int) -> Self:
        self.state = self.state + other
        return self

    def __isub__(self, other: int) -> Self:
        self.__iadd__(-other)
        return self

    def __eq__(self, other: int) -> bool:  # type: ignore
        return self.state == other

    def __lt__(self, other: int) -> bool:
        return self.state < other

    def __gt__(self, other: int) -> bool:
        return self.state > other

    def __le__(self, other: int) -> bool:
        return self == other or self < other

    def __ge__(self, other: int) -> bool:
        return self == other or self > other

    def __str__(self) -> str:
        rep = [
            f"{self.__class__}",
            f"Current state: {self.state}",
            f"State hsitory: {self.__state__}",
            f"Allowed states: {self.__allowed__}",
        ]

        if self.__state_names__ is not None:
            state_names = "\n".join(
                [f"{i_st}: {n_st}" for i_st, n_st in zip(self.__allowed__, self.__state_names__)]
            )
            rep.append("State names:")
            rep.append(state_names)

        return "\n".join(rep)

    def __repr__(self) -> str:
        return f"Current state: {self.state}"
