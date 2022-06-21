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
from datetime import date as python_date

# pylint: disable=import-error
# pylint: disable=no-name-in-module
from PySide6.QtCore import QDate
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QMenu
# pylint: enable=import-error
# pylint: enable=no-name-in-module


from .elements import add_action_buttons
from .elements import add_desc
from .elements import add_duedate
from .elements import add_name
from .elements import add_state
from .elements import State


class TaskEntry(QWidget):

    def __init__(self, task: dict):
        super().__init__()
        label = task['name'] + '\n' + 'Duedate: ' + task['duedate']
        self.button = QPushButton(label)
        self.button.setUpdatesEnabled(True)
        btn_name = 'projectbutton-' + task['state'].replace(' ', '')
        self.button.setObjectName(btn_name)
        self.button.setProperty('class', 'big_button')
        self.layout = QHBoxLayout(self)

        self.move_up = QPushButton('⇧')
        self.move_up.setProperty('class', 'big_button')
        self.move_up.setMaximumWidth(25)
        self.move_up.setObjectName('arrow')
        self.move_down = QPushButton('⇩')
        self.move_down.setProperty('class', 'big_button')
        self.move_down.setMaximumWidth(25)
        self.move_down.setObjectName('arrow')

        self.layout.addWidget(self.move_up, 1)
        self.layout.addWidget(self.move_down, 1)

        self.layout.addWidget(self.button, 10)

        self.menu = QMenu(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)
        self.task = task

    def update_fields(self):
        label = self.task['name'] + '\nDuedate: ' + self.task['duedate']
        self.button.setText(label)

    def on_context_menu(self, pos):
        self.menu.exec_(self.mapToGlobal(pos))


class TaskView(QWidget):
    def __init__(self):
        super().__init__()

        action_buttons = ['&Apply', '&Cancel', '&Delete']
        self.buttons = add_action_buttons(0, 0, 0, action_buttons)

        pn_layout, self.project_name = add_name()

        duedate_layout, self.duedate = add_duedate()
        self.duedate.dateChanged.connect(self.date_changed)

        state = add_state(creation_date=True)
        state_layout, self.state, self.created = state

        self.project_desc = add_desc()

        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.buttons['layout'])
        self.layout.addLayout(pn_layout)
        self.layout.addLayout(duedate_layout)
        self.layout.addLayout(state_layout)
        self.layout.addWidget(self.project_desc)

        self.update_date = False

    @Slot()
    def date_changed(self):
        self.update_date = True

    def set_data(self, project: dict):
        self.project_name.setText(project['name'])
        self.project_desc.setPlainText(project['description'])
        self.state.setCurrentText(project['state'])
        self.created.setText(project['creation_date'])
        date = QDate()
        if project['duedate'] == '':
            date = date.fromString(str(python_date.today()), format=Qt.ISODate)
        else:
            date = date.fromString(project['duedate'], format=Qt.ISODate)
        self.duedate.setDate(date)
        self.update_date = False

    def get_data(self) -> dict:
        data = {}
        data['name'] = self.project_name.text()
        data['description'] = self.project_desc.toPlainText()
        if self.update_date:
            data['duedate'] = self.duedate.date().toString(format=Qt.ISODate)
            self.update_date = False
        data['state'] = self.state.currentText()
        self.state.setCurrentText(State.TBD.value)
        # data['creation_date'] = self.created.text()

        return data
