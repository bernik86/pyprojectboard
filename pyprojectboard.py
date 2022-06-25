#!/usr/bin/env python3
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
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet
# pylint: enable=import-error

from pyprojectboard.qt_gui.qt_app import MainWindow


def main():
    app = QApplication()
    file_path = os.path.dirname(__file__)
    theme_fn = os.path.join(file_path, 'pyprojectboard/qt_gui/theme.xml')
    apply_stylesheet(app, theme=theme_fn)
    app.window = MainWindow()
    app.window.show()
    app.exec()


if __name__ == '__main__':
    main()
