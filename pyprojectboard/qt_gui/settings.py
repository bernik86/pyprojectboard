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
import os

# pylint: disable=import-error
# pylint: disable=no-name-in-module
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
# pylint: enable=import-error
# pylint: enable=no-name-in-module


def create_settings_page() -> QWidget:
    settings_page = QWidget()
    settings_page.settings = load_settings()

    settings_page.layout = QVBoxLayout()
    settings_page.layout_buttons = QHBoxLayout()
    settings_page.add_button = QPushButton('+')
    settings_page.remove_button = QPushButton('-')
    settings_page.up_button = QPushButton('⇧')
    settings_page.down_button = QPushButton('⇩')
    settings_page.rename_button = QPushButton('✍')

    settings_page.add_button.setShortcut(QKeySequence(Qt.ALT | Qt.Key_Plus))
    settings_page.remove_button.setShortcut(
        QKeySequence(Qt.ALT | Qt.Key_Minus))
    settings_page.up_button.setShortcut(QKeySequence(Qt.ALT | Qt.Key_W))
    settings_page.down_button.setShortcut(QKeySequence(Qt.ALT | Qt.Key_S))
    settings_page.rename_button.setShortcut(QKeySequence(Qt.ALT | Qt.Key_R))

    settings_page.layout_buttons.addWidget(settings_page.add_button)
    settings_page.layout_buttons.addWidget(settings_page.remove_button)
    settings_page.layout_buttons.addWidget(settings_page.up_button)
    settings_page.layout_buttons.addWidget(settings_page.down_button)
    settings_page.layout_buttons.addWidget(settings_page.rename_button)
    # settings_page.layout_buttons.addWidget(QPushButton('Export'))

    settings_page.setLayout(settings_page.layout)
    settings_page.layout.addWidget(QLabel('Projectboards:'))
    # settings_page.layout.addWidget(QLabel('Open:'))
    settings_page.list_projectboards = QListWidget()
    for file_name in settings_page.settings['@OPEN']:
        settings_page.list_projectboards.addItem(add_item(file_name))
    settings_page.layout.addWidget(settings_page.list_projectboards)

    settings_page.layout.addLayout(settings_page.layout_buttons)
    return settings_page


def load_settings() -> dict:
    config_path = '~/.config/pyprojectboard/'
    config_path = os.path.expanduser(config_path)
    config_fn = 'pyprojectboard.conf'
    config = os.path.join(config_path, config_fn)
    settings = {'@OPEN': []}

    if not os.path.isfile(config_fn):
        if not os.path.exists(config_path):
            os.makedirs(config_path)
        open(config, 'at').close()

    with open(config, 'rt', encoding='utf-8') as conf_file:
        lines = conf_file.readlines()

    item_type = ''
    for line in lines:
        if line.strip().startswith('@'):
            key = line.strip()
            settings[key] = []
            item_type = 'list'
            continue

        if item_type == 'list':
            settings[key].append(line.strip())

    return settings


def save_settings(settings: dict) -> None:
    config_fn = '~/.config/pyprojectboard/pyprojectboard.conf'
    config_fn = os.path.expanduser(config_fn)
    output = []

    for key in settings:
        if key.startswith('@'):
            output.append(key)
            for item in settings[key]:
                output.append(item)

    output = '\n'.join(output)
    with open(config_fn, 'wt', encoding='utf-8') as output_file:
        output_file.write(output)


def add_item(text: str) -> QListWidgetItem:
    item = QListWidgetItem()
    item.setText(text)
    return item
