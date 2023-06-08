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
from enum import Enum
from typing import Callable
from typing import Tuple

# pylint: disable=import-error
# pylint: disable=no-name-in-module
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QDateEdit
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QSizePolicy

# pylint: enable=import-error
# pylint: enable=no-name-in-module


class State(Enum):
    TBD = "to be determined"
    STARTED = "started"
    FINISHED = "finished"
    DISCARDED = "discarded"


finished_states = (State.FINISHED.value, State.DISCARDED.value)


def label_plus_line_edit(
    label_text: str, edit_text: str, edit_length: int
) -> Tuple[QHBoxLayout, QLineEdit]:
    label = QLabel(label_text)
    label.setMaximumWidth(150)
    label.setMinimumWidth(100)
    line_edit = QLineEdit()
    line_edit.setMaxLength(edit_length)
    line_edit.setMaximumWidth(500)
    line_edit.setMinimumWidth(250)
    line_edit.setText(edit_text)
    layout = QHBoxLayout()
    layout.addWidget(label)
    layout.addWidget(line_edit)
    layout.addStretch()

    return layout, line_edit


def label_plus_combobox(label_text: str) -> Tuple[QHBoxLayout, QComboBox]:
    label = QLabel(label_text)
    label.setMaximumWidth(150)
    label.setMinimumWidth(100)
    combo = QComboBox()
    for state in State:
        combo.addItem(state.value)
    layout = QHBoxLayout()
    layout.addWidget(label)
    layout.addWidget(combo)
    layout.addStretch()

    return layout, combo


def label_plus_stretch(label_text: str) -> QHBoxLayout:
    layout = QHBoxLayout()
    layout.addStretch(1)
    layout.addWidget(QLabel(label_text))
    layout.addStretch(1)

    return layout


def add_action_buttons(
    left: int = 20, right: int = 20, spacing: int = 6, button_list: list = None
) -> dict:
    if button_list is None:
        button_list = ["Save", "New", "Delete"]

    buttons = {}

    layout = QHBoxLayout()
    layout.addSpacing(left)

    for name in button_list:
        buttons[name] = QPushButton(name)
        buttons[name].setMaximumWidth(250)
        buttons[name].setMinimumWidth(150)
        layout.addWidget(buttons[name])
        layout.addSpacing(spacing)

    layout.insertStretch(len(button_list * 2) - 1)
    layout.addSpacing(right)
    buttons["layout"] = layout

    return buttons


def show_dialog(msg_text: str, msg_icon: int = QMessageBox.Warning) -> int:
    msg_box = QMessageBox()
    msg_box.setIcon(msg_icon)
    msg_box.setText(msg_text)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.Yes)
    answer = msg_box.exec()

    return answer


def add_name() -> Tuple[QHBoxLayout, QLineEdit]:
    label = QLabel("Name:")
    label.setMaximumWidth(150)
    label.setMinimumWidth(100)
    line_edit = QLineEdit()
    line_edit.setMaxLength(32)
    line_edit.setMaximumWidth(500)
    line_edit.setMinimumWidth(250)
    layout = QHBoxLayout()
    layout.addWidget(label)
    layout.addWidget(line_edit)
    layout.addStretch()
    return layout, line_edit


def add_duedate() -> Tuple[QHBoxLayout, QDateEdit]:
    duedate_layout = QHBoxLayout()
    label = QLabel("Duedate:")
    label.setMinimumWidth(100)
    label.setMaximumHeight(150)
    duedate_layout.addWidget(label)
    duedate = QDateEdit()
    duedate.setCalendarPopup(True)
    duedate.setDisplayFormat("yyyy-MM-dd")
    duedate_layout.addWidget(duedate)
    duedate_layout.addStretch()

    return duedate_layout, duedate


def add_state(creation_date=True) -> Tuple[QHBoxLayout, QComboBox, QLabel]:
    label = QLabel("State:")
    label.setMaximumWidth(150)
    label.setMinimumWidth(100)
    combo = QComboBox()
    for state in State:
        combo.addItem(state.value)
    combo.setCurrentText(State.TBD.value)
    layout = QHBoxLayout()
    layout.addWidget(label)
    layout.addWidget(combo)

    ret = [layout, combo, None]
    if creation_date:
        layout.addSpacing(15)
        layout.addWidget(QLabel("Created: "))
        created = QLabel()
        layout.addWidget(created)
        ret[-1] = created

    layout.addStretch()

    return ret


def add_desc() -> QTextEdit:
    desc = QTextEdit()
    desc.createStandardContextMenu()
    desc.setAcceptRichText(False)

    return desc


def add_action(text: str, parent, connect_to: Callable = None) -> QAction:
    action = QAction(text, parent)
    if connect_to is not None:
        action.triggered.connect(connect_to)
    return action


def add_button(text: str, connect_to: Callable) -> QPushButton:
    button = QPushButton(text)
    button.clicked.connect(connect_to)
    return button


def add_projectboard_description(
    left: int = 20, right: int = 20
) -> Tuple[QVBoxLayout, QPushButton, QTextEdit]:
    vert_layout = QVBoxLayout()
    layout = QHBoxLayout()
    layout.setAlignment(Qt.AlignTop)
    layout.addSpacing(left)

    edit = QPushButton("✍")
    edit.setMaximumWidth(50)

    layout.addWidget(QLabel("Description:"))

    layout.addSpacing(right)
    vert_layout.addLayout(layout)
    layout_2 = QHBoxLayout()
    layout_2.setAlignment(Qt.AlignTop)
    layout_2.addSpacing(left)

    desc = QTextEdit()
    desc.setMinimumHeight(40)
    desc.setMaximumHeight(130)
    desc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    layout_2.addWidget(desc)
    layout_2.addSpacing(right + 5)
    vert_layout.addLayout(layout_2)

    return vert_layout, edit, desc
