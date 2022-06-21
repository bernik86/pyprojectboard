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
from dataclasses import dataclass, field, InitVar
from functools import partial

# pylint: disable=import-error
# pylint: disable=no-name-in-module
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout
from PySide6.QtWidgets import QScrollArea, QPushButton
from PySide6.QtWidgets import QProgressBar
from PySide6.QtCore import Slot
from PySide6.QtCore import QDate, Qt
# pylint: enable=import-error
# pylint: enable=no-name-in-module

from ..data.data import ProjectList, Project
from ..export.latex import export
from .elements import add_action
from .elements import add_action_buttons
from .elements import add_desc
from .elements import add_duedate
from .elements import add_name
from .elements import add_state
from .elements import add_projectboard_description
from .elements import label_plus_stretch
from .elements import show_dialog
from .elements import State
from .task_views import TaskEntry
from .task_views import TaskView


class ProjectEntry(QWidget):

    def __init__(self, project: dict):
        super().__init__()
        pol = QSizePolicy()
        self.setSizePolicy(pol.Expanding, pol.Minimum)

        self.project = dict(project)
        self.layout = QHBoxLayout(self)

        self.move_up = QPushButton('⇧')
        self.move_up.setMaximumWidth(50)
        self.move_up.setObjectName('arrow')
        self.move_down = QPushButton('⇩')
        self.move_down.setMaximumWidth(50)
        self.move_down.setObjectName('arrow')

        self.project_name = QPushButton(project['name'])
        self.project_name.setSizePolicy(QSizePolicy.Expanding,
                                        QSizePolicy.Maximum)
        button_state = 'projectbutton-' + project['state'].replace(' ', '')
        self.project_name.setObjectName(button_state)
        self.progress = QProgressBar()
        self.progress.setValue(project['progress'])
        self.progress.setSizePolicy(QSizePolicy.Maximum,
                                    QSizePolicy.Maximum)
        self.progress.setMaximumWidth(400)
        self.progress.setMinimumWidth(300)
        self.progress.setMaximumHeight(25)

        dd_label = 'Duedate: '
        if project['duedate'] != '':
            dd_label += project['duedate']
        else:
            dd_label += 'None'
        dd_label.ljust(30)
        self.duedate = QLabel(dd_label)
        self.duedate.setMinimumWidth(200)

        self.layout.addWidget(self.move_up)
        self.layout.addWidget(self.move_down)
        self.layout.addWidget(self.project_name)
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.duedate)

        self.layout.setSpacing(20)

    def update_fields(self) -> None:
        if self.project['duedate'] != '':
            dd_label = 'Duedate: ' + self.project['duedate']
            self.duedate.setText(dd_label)
        self.progress.setValue(self.project['progress'])


class PageManager(QScrollArea):
    def __init__(self, project_list: ProjectList):
        super().__init__()
        self.views = Views(projectboard=project_list)
        self.setWidget(self.views.projectboard_view)
        self.setWidgetResizable(True)
        self.connect_views_buttons()
        self.current_pid = None
        self.current_tid = None
        self.project_list = project_list
        self._sender = None
        self._task_sender = None

    def connect_views_buttons(self) -> None:
        # ProjectListView buttons
        save = self.views.projectboard_view.buttons['&Save']
        save.clicked.connect(self.save_button_clicked)

        add = self.views.projectboard_view.buttons['Add &Project']
        add.clicked.connect(self.projectlist_view_add_clicked)

        export_btn = self.views.projectboard_view.buttons['&Export']
        export_btn.clicked.connect(self.projectlist_view_export_clicked)

        for child in self.views.projectboard_view.children():
            if isinstance(child, ProjectEntry):
                button = child.project_name
                button.clicked.connect(self.on_project_button_clicked)
                self.connect_project_entry_buttons(child)

        # ProjectView buttons
        app = self.views.project_view.buttons['&Apply']
        app.clicked.connect(self.project_view_apply_clicked)

        cancel = self.views.project_view.buttons['&Cancel']
        cancel.clicked.connect(self.project_view_cancel_clicked)

        add = self.views.project_view.buttons['Add &Task']
        add.clicked.connect(self.project_view_add_task_clicked)

        delete = self.views.project_view.buttons['&Delete']
        delete.clicked.connect(self.project_view_delete_clicked)

        # TaskView buttons
        app = self.views.task_view.buttons['&Apply']
        app.clicked.connect(self.task_view_apply_clicked)

        cancel = self.views.task_view.buttons['&Cancel']
        cancel.clicked.connect(self.task_view_cancel_clicked)

        delete = self.views.task_view.buttons['&Delete']
        delete.clicked.connect(self.task_view_delete_clicked)

    def switch_from_project_view_to_projectlist_view(self) -> None:
        self.current_pid = None
        self._sender = None
        self.views.project_view = self.takeWidget()
        self.views.project_view.reset()
        self.setWidget(self.views.projectboard_view)

    def switch_from_projectlist_view_to_project_view(
            self,
            project: dict) -> None:

        self.views.project_view.reset()
        self.current_pid = project['_id']
        self.project_list.project(self.current_pid, project)
        tasks = []
        for tid in project['task_ids']:
            task_dict = {}
            self.project_list.task(tid, self.current_pid, task_dict)
            tasks.append(task_dict)

        self.views.project_view.set_data(project, tasks)
        for child in self.views.project_view.children():
            if isinstance(child, TaskEntry):
                child.button.clicked.connect(self.task_button_clicked)
                self.add_task_menu(child)

        self.views.projectboard_view = self.takeWidget()
        self.setWidget(self.views.project_view)

    @Slot()
    def projectlist_view_add_clicked(self):
        project = {}
        project['creation_date'] = str(python_date.today())
        self.project_list.project(None, project, 'new')
        self.current_pid = project['_id']
        new_entry = self.views.projectboard_view.add_project_entry(project)
        new_entry.project_name.clicked.connect(self.on_project_button_clicked)
        new_entry.update_date = False
        self.views.project_view.buttons['&Cancel'].setEnabled(False)
        self.views.project_view.buttons['Add &Task'].setEnabled(False)
        self._sender = new_entry
        self.connect_project_entry_buttons(new_entry)
        self.switch_from_projectlist_view_to_project_view(project)

    @Slot()
    def projectlist_view_export_clicked(self):
        export(self.views.projectboard, True)

    @Slot()
    def on_project_button_clicked(self):
        self.views.project_view.buttons['&Cancel'].setEnabled(True)
        self.views.project_view.buttons['Add &Task'].setEnabled(True)
        self._sender = self.sender().parent()
        if self._sender.project_name.objectName().find('projectbutton') > -1:
            project = self._sender.project
        self.switch_from_projectlist_view_to_project_view(project)

    @Slot()
    def project_view_apply_clicked(self):
        project = self.views.project_view.get_data()
        self.project_list.project(self.current_pid, project, 'set')
        self.project_list.project(self.current_pid, project, 'prg')
        self._sender.project_name.setText(project['name'])
        self._sender.project.update(project)
        # self.project_list.project(self.current_pid, project, 'set')
        button_state = 'projectbutton-' + project['state'].replace(' ', '')
        self._sender.project_name.setObjectName(button_state)
        self._sender.update_fields()
        self.switch_from_project_view_to_projectlist_view()

    @Slot()
    def project_view_cancel_clicked(self):
        answer = show_dialog('Do you want to discard any changes?')
        if answer == QMessageBox.Yes:
            self.switch_from_project_view_to_projectlist_view()

    @Slot()
    def project_view_delete_clicked(self):
        answer = show_dialog('Do you really want to delete this project?')
        if answer == QMessageBox.Yes:
            pids = self.views.projectboard.get_ids()
            widget_id = pids.index(self.current_pid)
            pids.pop(widget_id)
            children = self.views.projectboard_view.children()
            entries = [child for child in children
                       if isinstance(child, ProjectEntry)]

            widget = entries[widget_id]
            self.views.projectboard_view.layout.removeWidget(widget)
            widget.deleteLater()
            self.project_list.project(self.current_pid, {}, 'del')
            self.switch_from_project_view_to_projectlist_view()

    @Slot()
    def save_button_clicked(self):
        desc = self.views.projectboard_view.pb_desc[2].toPlainText()
        self.project_list.set_metadata('description', desc)
        self.project_list.save_data()

    def switch_from_project_view_to_task_view(self, task: dict) -> None:
        self.views.task_view.set_data(task)
        self.views.project_view = self.takeWidget()
        self.setWidget(self.views.task_view)

    def switch_from_task_view_to_project_view(self) -> None:
        data = {}
        self.project_list.project(self.current_pid, data, 'prg')
        self._sender.progress.setValue(data['progress'])
        self._task_sender = None
        self.current_tid = None
        self.views.task_view.state.setCurrentText(State.TBD.value)
        self.views.task_view = self.takeWidget()
        self.setWidget(self.views.project_view)

    @Slot()
    def task_button_clicked(self):
        self.views.task_view.buttons['&Cancel'].setEnabled(True)
        self._task_sender = self.sender().parent()
        task = self._task_sender.task
        self.current_tid = task['_id']
        self.switch_from_project_view_to_task_view(task)

    @Slot()
    def task_view_apply_clicked(self):
        task = self.views.task_view.get_data()
        task['_id'] = self.current_tid
        self._task_sender.button.setText(task['name'])
        self._task_sender.task.update(task)
        self.project_list.task(self.current_tid,
                               self.current_pid, task, 'set')
        button_state = 'projectbutton-' + task['state'].replace(' ', '')
        self._task_sender.button.setObjectName(button_state)
        self._task_sender.update_fields()
        self.switch_from_task_view_to_project_view()

    @Slot()
    def task_view_cancel_clicked(self):
        answer = show_dialog('Do you want to discard any changes?')
        if answer == QMessageBox.Yes:
            self.switch_from_task_view_to_project_view()

    @Slot()
    def task_view_delete_clicked(self):
        answer = show_dialog('Do you really want to delete this task?')
        if answer == QMessageBox.Yes:
            widget = self._task_sender
            self.project_list.task(self.current_tid,
                                   self.current_pid, {}, 'del')
            widget.deleteLater()
            self.switch_from_task_view_to_project_view()

    @Slot()
    def project_view_add_task_clicked(self):
        task = {'creation_date': str(python_date.today())}
        self.project_list.task(None, self.current_pid, task, 'new')
        self.current_tid = task['_id']
        new_entry = self.views.project_view.add_task_entry(task)
        new_entry.button.clicked.connect(self.task_button_clicked)
        new_entry.update_date = False
        self.add_task_menu(new_entry)
        self.views.task_view.buttons['&Cancel'].setEnabled(False)
        self._task_sender = new_entry
        self.switch_from_project_view_to_task_view(task)

    def add_task_menu(self, task_entry: TaskEntry) -> None:

        @Slot()
        def move_task(moveby: int):
            project_view = self.views.project_view
            layout = project_view.layout_right
            self.project_list.project(self.current_pid, project := {})
            task_ids = project['task_ids']
            n_tasks = len(task_ids)
            tid = task_entry.task['_id']
            # tid = self.current_tid
            idx = task_ids.index(tid)
            idx2 = idx - moveby

            idx2 = max(idx2, 0)
            idx2 = min(idx2, n_tasks - 1)

            if idx2 != idx:
                task_ids.insert(idx2, task_ids.pop(idx))
                self.project_list.project(self.current_pid, project, 'set')
                layout.removeWidget(task_entry)
                layout.insertWidget(idx2 + 1, task_entry)

        @Slot()
        def set_task_state(new_state: str):
            task_entry.task['state'] = new_state
            state_name = task_entry.task['state'].replace(' ', '')
            btn_name = 'projectbutton-' + state_name
            task_entry.button.setObjectName(btn_name)
            task_entry.button.setStyle(task_entry.button.style())
            self.project_list.task(task_entry.task['_id'],
                                   self.current_pid,
                                   dict(task_entry.task), 'set')
            self.project_list.project(self.current_pid, {}, 'prg')

        menu_entries = (("Move to top", partial(move_task, 50000)),
                        ("Move up 5 places", partial(move_task, 5)),
                        ("----------------------------------", None),
                        ("Set state: started",
                         partial(set_task_state, State.STARTED.value)),
                        ("Set state: finished",
                         partial(set_task_state, State.FINISHED.value)),
                        ("----------------------------------", None),
                        ("Move down 5 places", partial(move_task, -5)),
                        ("Move to bottom", partial(move_task, -50000)))

        for entry, connect in menu_entries:
            task_entry.menu.addAction(add_action(entry,
                                                 task_entry,
                                                 connect))

        task_entry.move_up.clicked.connect(partial(move_task, 1))
        task_entry.move_down.clicked.connect(partial(move_task, -1))

    def connect_project_entry_buttons(
            self,
            project_entry: ProjectEntry):

        @Slot()
        def move_project(moveby):
            pid = project_entry.project['_id']
            layout = self.views.projectboard_view.layout
            n_projects = len(self.project_list.get_ids())
            idx = layout.indexOf(project_entry)
            idx2 = idx + moveby

            if 1 < idx <= n_projects + 1 and 1 < idx2 <= n_projects + 1:
                self.project_list.project(pid, {'moveby': moveby}, 'mov')
                widget = layout.takeAt(idx)
                layout.insertItem(idx2, widget)

        project_entry.move_up.clicked.connect(partial(move_project, -1))
        project_entry.move_down.clicked.connect(partial(move_project, 1))


class ProjectListView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.pb_desc = add_projectboard_description(10, 10)

        button_list = ['&Save', 'Add &Project', '&Export', '&Close']
        self.buttons = add_action_buttons(10, 10, button_list=button_list)
        self.layout.addLayout(self.buttons['layout'])
        self.layout.addLayout(self.pb_desc[0])

    def add_project_entry(self, project: dict) -> ProjectEntry:
        n_widgets = sum(1 for widg in self.children()
                        if isinstance(widg, ProjectEntry))

        self.layout.insertWidget(n_widgets + 2, entry := ProjectEntry(project))

        return entry

    def set_data(self, project_list: ProjectList) -> None:
        desc = project_list.get_metadata('description')
        self.pb_desc[2].setText(desc)
        pids = project_list.get_ids()
        for pid in pids:
            project_list.project(pid, project := {})
            project_list.project(pid, project, 'prg')
            self.layout.addWidget(ProjectEntry(project))

        self.layout.addStretch()


class ProjectView(QWidget):
    def __init__(self):
        super().__init__()

        action_buttons = ['&Apply', '&Cancel', 'Add &Task', '&Delete']
        self.buttons = add_action_buttons(0, 0, 0, action_buttons)

        pn_layout, self.project_name = add_name()

        duedate_layout, self.duedate = add_duedate()
        self.duedate.dateChanged.connect(self.date_changed)

        state = add_state(creation_date=True)
        state_layout, self.state, self.created = state

        self.project_desc = add_desc()

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.buttons['layout'])
        self.layout.addLayout(pn_layout)
        self.layout.addLayout(duedate_layout)
        self.layout.addLayout(state_layout)
        self.layout.addWidget(self.project_desc)

        self.layout_right = QVBoxLayout()
        self.layout_right.addLayout(label_plus_stretch('Tasks'))
        self.layout_right.setAlignment(Qt.AlignTop)

        self.h_layout = QHBoxLayout(self)
        self.h_layout.addLayout(self.layout, 8)
        self.h_layout.addLayout(self.layout_right, 5)

        self.update_date = False

    @Slot()
    def date_changed(self):
        self.update_date = True

    def set_data(self, project: dict, tasks: list[dict]) -> None:
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

        for task in tasks:
            task_entry = TaskEntry(task)
            self.layout_right.insertWidget(-1, task_entry)

        self.update()

    def get_data(self) -> dict:
        data = {}
        data['name'] = self.project_name.text()
        data['description'] = self.project_desc.toPlainText()
        if self.update_date:
            data['duedate'] = self.duedate.date().toString(format=Qt.ISODate)
            self.update_date = False
        data['state'] = self.state.currentText()
        self.state.setCurrentText(State.TBD.value)
        for child in self.children():
            if isinstance(child, TaskEntry):
                self.layout_right.removeWidget(child)
                child.deleteLater()

        return data

    def add_task_entry(self, task: dict) -> TaskEntry:
        task_entry = TaskEntry(task)
        self.layout_right.insertWidget(1, task_entry)
        return task_entry

    def reset(self) -> None:
        self.set_data(Project().as_dict(), [])
        for child in self.children():
            if isinstance(child, TaskEntry):
                self.layout_right.removeWidget(child)
                child.deleteLater()


@dataclass
class Views():

    projectboard_view: ProjectListView = field(default_factory=ProjectListView)
    project_view: ProjectView = field(default_factory=ProjectView)
    task_view: TaskView = field(default_factory=TaskView)
    projectboard: InitVar[dict] = None

    def __post_init__(self, projectboard):
        self.projectboard_view.set_data(projectboard)
        self.projectboard = projectboard
