#! python
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


# pylint: disable=import-error, no-name-in-module
# isort: split
import os

# Import of QtWebEngineQuick needed to resolve the following warning:
# Attribute Qt::AA_ShareOpenGLContexts must be set before QCoreApplication is created.
from PySide6 import QtWebEngineQuick  # type: ignore  # pylint: disable=unused-import
from PySide6.QtWidgets import QApplication  # type: ignore

from gui.qt.main_window import MainWindow  # type: ignore

# pylint: enable=import-error, no-name-in-module


def main():
    # Set environment variable to get rid of the following warning:
    # QApplication: invalid style override 'kvantum' passed, ignoring it.
    os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
    app = QApplication()
    app.window = MainWindow()
    app.window.show()
    app.exec()


if __name__ == "__main__":
    import sys

    sys.exit(main())
