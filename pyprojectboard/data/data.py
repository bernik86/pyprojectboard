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
import abc
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
from typing import TypeVar

from ..qt_gui.elements import finished_states

from .custom_dict import OrderableDict

ProjectList = TypeVar('ProjectList')
ENC = 'utf-8'


def create_id() -> str:
    '''Function to create ID based on current time.'''
    return str(datetime.now()).replace(' ', '-')


@dataclass
class ProjectListInterface(abc.ABC):
    """
    Abstract class usedas template for implementation of project
    list data structre.

    TODO: specify properties that a dataset must implement!
    """

    @abc.abstractmethod
    def save_data(self) -> None:
        """Save data (e.g., to file)."""

    @abc.abstractmethod
    def load_data(self) -> None:
        """Load data (e.g., group file)."""

    @abc.abstractmethod
    def get_ids(self, group: str = 'projects') -> list[str]:
        """Collect project or task IDs and return them as a list.

        Argument:
        group -- specify whether the IDs of projects (group='projects') or
                  tasks (group='tasks') should be returned.
        """

    @abc.abstractmethod
    def set_metadata(self, key: str, value: str) -> None:
        """Set project lists metadata, e.g., name or filename.

        Arguments:
        field -- name of the metadata property to set.
        value -- value to which the metadata property is set.
        """

    @abc.abstractmethod
    def get_metadata(self, key: str) -> str:
        """Get project lists metadata, e.g., name or filename.

        Argument:
        field -- name of the metadata property to get.

        Return:
        Value of metadata property.
        """

    @abc.abstractmethod
    def project(self, pid: str, data: dict, action='get') -> None:
        """Perform action on project data.

        Arguments:
        pid -- ID of the project
        data -- dict for data exchange between frontend and backend.
        action -- action to be performed on the data:
                    * 'get' ->  return project data
                    * 'set' ->  set project data
                    * 'new' ->  create new (empty) project and return
                                data as dict
                    * 'del' ->  delete project
                    * 'prg' ->  calculate and update progress of project
                    * 'mov' ->  move project; data needs to contain key
                                'moveby', the value of which determines
                                how far the project should be moved.
        """

    @abc.abstractmethod
    def task(self, tid: str, pid: str, data: dict, action='get') -> None:
        """Perform action on project data.

        Arguments:
        tid -- Task ID
        pid -- ID of the project
        data -- dict for data exchange between frontend and backend.
        action -- action to be performed on the data:
                    * 'get' ->  return task data
                    * 'set' ->  set task data
                    * 'new' ->  create new (empty) project and return
                                data as dict
                    * 'upd' ->  update existing task data
                    * 'del' ->  delete task
        """


@dataclass
class ProjectList(ProjectListInterface):

    _metadata: dict = field(default_factory=dict)
    _projects: dict = field(default_factory=OrderableDict)
    _tasks: dict = field(default_factory=dict)

    def save_data(self) -> None:
        jstr = []
        jstr.append(json.dumps({'METADATA': self._metadata}))

        for project in self._projects.values():
            jstr.append(json.dumps({'Project': project.__dict__}))

        for task in self._tasks.values():
            jstr.append(json.dumps({'Task': task.__dict__}))

        with open(self._metadata['filename'], 'wt', encoding=ENC) as save:
            save.write('\n'.join(jstr))

    def load_data(self, filename: str = None) -> None:

        if filename is None:
            try:
                filename = self._metadata['filename']
            except KeyError:
                print('No filenme specified!')
                return

        try:
            with open(self._metadata['filename'], 'rt', encoding=ENC) as load:
                data = load.readlines()
        except FileNotFoundError:
            pass
        else:
            for line in data:
                jstr = json.loads(line)
                key = next(iter(jstr.keys()))

                if key == 'METADATA':
                    self._metadata = jstr[key]
                    continue
                if key == 'Project':
                    current_dict = self._projects
                    item = Project()
                elif key == 'Task':
                    current_dict = self._tasks
                    item = Task()
                else:
                    continue

                item.__dict__ = jstr[key]
                current_dict[item.id] = item
            self._metadata['filename'] = filename

    def get_ids(self, group: str = 'projects') -> list[str]:
        """Collect project or task IDs and return them as a list.

        Argument:
        group -- specify whether the IDs of projects (group='projects') or
                  tasks (group='tasks') should be returned.
        """
        if group == 'projects':
            return list(self._projects.keys())

        if group == 'tasks':
            return list(self._tasks.keys())

        return list(self._metadata.keys())

    def set_metadata(self, key: str, value: str) -> None:
        """Set project lists metadata, e.g., name or filename.

        Arguments:
        field -- name of the metadata property to set.
        value -- value to which the metadata property is set.
        """
        self._metadata[key] = value

    def get_metadata(self, key: str) -> str:
        """Get project lists metadata, e.g., name or filename.

        Argument:
        field -- name of the metadata property to get.

        Return:
        Value of metadata property.
        """
        try:
            value = self._metadata[key]
        except KeyError:
            value = ''
        return value

    def project(self, pid: str, data: dict, action='get') -> None:
        """Perform action on project data.

        Arguments:
        pid -- ID of the project
        data -- dict for data exchange between frontend and backend.
        action -- action to be performed on the data:
                    * 'get' ->  return project data
                    * 'set' ->  set project data
                    * 'new' ->  create new (empty) project and return
                                data as dict
                    * 'del' ->  delete project
                    * 'prg' ->  calculate and update progress of project
                    * 'mov' ->  move project; data needs to contain key
                                'moveby', the value of which determines
                                how far the project should be moved.
        """

        if action == 'get':
            data.update(self._projects[pid].as_dict())

        elif action == 'set':
            try:
                data.pop('_id')
            except KeyError:
                pass
            self._projects[pid].__dict__.update(data)

        elif action == 'new':
            new_project = Project()
            if len(data):
                new_project.__dict__.update(data)
            self._projects[new_project.id] = new_project
            data.update(new_project.as_dict())

        elif action == 'del':
            for tid in self._projects[pid].task_ids:
                self.task(tid, pid, data, 'del')
            project = self._projects.pop(pid)
            data.update(project.as_dict())

        elif action == 'prg':
            tids = self._projects[pid].task_ids
            n_tasks = len(tids)
            if n_tasks > 0:
                n_finished = sum(1 for tid in tids
                                 if self._tasks[tid].state in finished_states)
                data['progress'] = n_finished / n_tasks * 100
            else:
                prg = self._projects[pid].state in finished_states
                data['progress'] = prg * 100
            try:
                self._projects[pid].progress = data['progress']
            except KeyError:
                print('Error: project ' + pid + 'does not exist!')

        elif action == 'mov':
            self._projects.move(pid, data['moveby'])

    def task(self, tid: str, pid: str, data: dict, action='get') -> None:
        """Perform action on project data.

        Arguments:
        tid -- Task ID
        pid -- ID of the project
        data -- dict for data exchange between frontend and backend.
        action -- action to be performed on the data:
                    * 'get' ->  return task data
                    * 'set' ->  set task data
                    * 'new' ->  create new (empty) project and return
                                data as dict
                    * 'del' ->  delete task
        """
        if action == 'get':
            data.update(self._tasks[tid].as_dict())
        elif action == 'set':
            try:
                data.pop('_id')
            except KeyError:
                pass
            self._tasks[tid].__dict__.update(data)
            if tid not in self._projects[pid].task_ids:
                self._projects[pid].task_ids.append(tid)
        elif action == 'new':
            new_task = Task()
            if len(data):
                new_task.__dict__.update(data)
            self._tasks[new_task.id] = new_task
            self._projects[pid].task_ids.insert(0, new_task.id)
            data.update(new_task.as_dict())
        elif action == 'del':
            try:
                self._projects[pid].task_ids.remove(tid)
            except ValueError:
                print('Project ' + pid + ' has not task with ID ' + tid)
            else:
                task = self._tasks.pop(tid)
                data.update(task.as_dict())


@dataclass
class Project:
    """Class containing project data"""

    name: str = ''
    description: str = ''
    duedate: str = ''
    creation_date: str = ''
    state: str = ''
    progress: float = 0.0
    _id: str = field(default_factory=create_id)
    task_ids: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        # pylint: disable=invalid-name
        return self._id

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class Task(Project):
    """Class containg task data"""

    def __post_init__(self):
        self.task_ids = None
