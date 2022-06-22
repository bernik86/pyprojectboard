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
from functools import partial
import os

# pylint: disable=import-error
# pylint: disable=no-name-in-module
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QInputDialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Slot
# pylint: enable=import-error
# pylint: enable=no-name-in-module

from ..data.data import ProjectList
from .project_views import PageManager
from .settings import create_settings_page
from .settings import save_settings
from .settings import add_item


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        file_path = os.path.dirname(__file__)
        style_fn = os.path.join(file_path, 'style.qss')

        with open(style_fn, 'r', encoding='utf-8') as style_file:
            style = style_file.read()
            self.setStyleSheet(style)

        self.setMinimumWidth(1200)
        self.setMinimumHeight(768)
        # self.window.showMaximized()

        self.tabs = QTabWidget(self)
        self.tabs.setSizePolicy(QSizePolicy.Expanding,
                                QSizePolicy.Expanding)

        self.settings_page = self.init_settings_page()
        self.tabs.addTab(self.settings_page, r"⚙")

        for item in self.settings_page.settings['@OPEN']:
            pb_name, file_name = item.rsplit(':', 1)
            projectboard = add_pb_instance(pb_name, file_name, True)

            if projectboard is not None:
                page_manager = PageManager(projectboard)
                self.tabs.addTab(page_manager, pb_name)
                self.connect_close_button(page_manager)

        self.setCentralWidget(self.tabs)

    def init_settings_page(self):

        settings_page = create_settings_page()
        add_button = settings_page.add_button
        rm_button = settings_page.remove_button
        rename_button = settings_page.rename_button
        up_button = settings_page.up_button
        down_button = settings_page.down_button
        pb_list = settings_page.list_projectboards

        add_button.clicked.connect(self.add_projectboard)
        rm_button.clicked.connect(self.projectlist_view_close_clicked)
        rename_button.clicked.connect(self.rename_projectboard)
        up_button.clicked.connect(partial(self.move_pb, -1))
        down_button.clicked.connect(partial(self.move_pb, 1))
        pb_list.itemDoubleClicked.connect(self.switch_to_projectboard)

        return settings_page

    @Slot()
    def projectlist_view_close_clicked(self):

        idx = self.tabs.currentIndex() - 1
        if idx < 0:
            idx = self.settings_page.list_projectboards.currentRow()

        if idx > -1:
            page_manager = self.tabs.widget(idx + 1)
            self.settings_page.list_projectboards.takeItem(idx)
            self.settings_page.settings['@OPEN'].pop(idx)
            save_settings(self.settings_page.settings)
            self.tabs.removeTab(idx + 1)
            self.tabs.setCurrentIndex(0)
            page_manager.deleteLater()

    def connect_close_button(self, page_manager):
        button = page_manager.views.projectboard_view.buttons['&Close']
        button.clicked.connect(self.projectlist_view_close_clicked)

    @Slot()
    def add_projectboard(self):
        directory = os.path.expanduser('~/')
        options = QFileDialog.DontConfirmOverwrite
        file_name = QFileDialog.getSaveFileName(caption='Choose file',
                                                dir=directory,
                                                options=options)
        if not file_name[1]:
            return

        if os.path.isfile(file_name[0]):
            projectboard = add_pb_instance(None, file_name[0], True)
            if projectboard is None:
                info = QMessageBox()
                info.setText(' '.join([file_name[0],
                                       "is not a valid",
                                       "PyProjectBoard file!",
                                       "File not read!"]))
                info.setIcon(QMessageBox.Critical)
                info.exec()
                return

            pb_name = projectboard.get_metadata('name')

        elif file_name[0]:
            pb_name = os.path.basename(file_name[0])
            projectboard = add_pb_instance(pb_name, file_name[0], False)
            projectboard.save_data()

        joint_name = ':'.join((pb_name, file_name[0]))
        if joint_name not in self.settings_page.settings['@OPEN']:
            page_manager = PageManager(projectboard)
            self.tabs.addTab(page_manager, pb_name)
            self.connect_close_button(page_manager)
            self.settings_page.settings['@OPEN'].append(joint_name)
            item = add_item(joint_name)
            self.settings_page.list_projectboards.addItem(item)

        item_idx = self.settings_page.settings['@OPEN'].index(joint_name)
        self.tabs.setCurrentIndex(item_idx + 1)
        save_settings(self.settings_page.settings)

    @Slot()
    def switch_to_projectboard(self):
        item_idx = self.settings_page.list_projectboards.currentRow()
        item_idx = item_idx + 1
        self.tabs.setCurrentIndex(item_idx)

    @Slot()
    def rename_projectboard(self):

        item_idx = self.settings_page.list_projectboards.currentRow()
        if item_idx == -1:
            message_text = "Please select projectboard to rename from"
            message_text += " list of open projectboards!"
            msg = QMessageBox(icon=QMessageBox.Information,
                              parent=self)
            msg.setText(message_text)
            msg.exec()
            return

        item = self.settings_page.list_projectboards.currentItem()
        item_text = item.text()
        pb_name, file_name = item_text.strip().rsplit(':', 1)

        inp = QInputDialog(parent=self)
        inp.setWindowTitle("Rename projectboard")
        inp.setInputMode(QInputDialog.TextInput)
        inp.setLabelText("Name:")
        inp.setTextValue(pb_name)
        line_edit = inp.children()[0]
        line_edit.setMaxLength(32)
        line_edit.setMaximumWidth(500)
        line_edit.setMinimumWidth(250)
        response_ok = inp.exec()
        new_name = inp.textValue().strip()

        if response_ok and new_name != pb_name:
            full_name = ':'.join((new_name, file_name))
            item.setText(full_name)
            idx = self.settings_page.settings['@OPEN'].index(item_text)
            self.tabs.setTabText(item_idx + 1, new_name)
            self.settings_page.settings['@OPEN'][idx] = full_name
            page_manager = self.tabs.widget(item_idx + 1)
            page_manager.views.projectboard.set_metadata('name', new_name)
            page_manager.views.projectboard.save_data()
            save_settings(self.settings_page.settings)

    @Slot()
    def move_pb(self, moveby: int):
        item_idx = self.settings_page.list_projectboards.currentRow()
        if item_idx == -1:
            return

        new_idx = item_idx + moveby
        n_open = len(self.settings_page.settings['@OPEN'])
        if new_idx < 0 or new_idx >= n_open:
            return

        item = self.settings_page.list_projectboards.takeItem(item_idx)
        self.settings_page.list_projectboards.insertItem(new_idx, item)
        self.settings_page.list_projectboards.setCurrentRow(new_idx)
        item_text = item.text()
        pb_name, _ = item_text.strip().rsplit(':', 1)
        page_manager = self.tabs.widget(item_idx + 1)
        self.tabs.removeTab(item_idx + 1)
        self.tabs.insertTab(new_idx + 1, page_manager, pb_name)
        self.settings_page.settings['@OPEN'].pop(item_idx)
        self.settings_page.settings['@OPEN'].insert(new_idx, item_text)
        save_settings(self.settings_page.settings)


def add_pb_instance(name: str, filename: str, load_data: bool):
    projectboard = ProjectList()
    projectboard.set_metadata('filename', filename)

    if load_data:
        try:
            projectboard.load_data()
        except ValueError:
            print("Not able to load data!")
            return None

    if name is not None:
        projectboard.set_metadata('name', name)

    return projectboard
