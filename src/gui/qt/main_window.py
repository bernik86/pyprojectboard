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
import os
from functools import partial
from typing import Dict
from typing import List
from typing import Optional

# pylint: disable=import-error
# pylint: disable=no-name-in-module
from PySide6 import QtCore  # type: ignore
from PySide6 import QtUiTools
from PySide6.QtCore import Qt  # type: ignore
from PySide6.QtWidgets import QFileDialog  # type: ignore
from PySide6.QtWidgets import QHeaderView
from PySide6.QtWidgets import QInputDialog
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtWidgets import QWidget

from data import settings  # type: ignore
from data.data import Projectboard  # type: ignore
from data.data import generate_id
from data.data import read_metadata
from data.state import StateInt  # type: ignore

# pylint: enable=import-error
# pylint: enable=no-name-in-module


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        file_path = os.path.dirname(__file__)
        style_fn = os.path.join(file_path, "style.qss")

        with open(style_fn, "r", encoding="utf-8") as style_file:
            style = style_file.read()
            self.setStyleSheet(style)

        self.setWindowTitle("PyProjectBoard V2.0 ALPHA")
        self.tabs = QTabWidget(self)
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.settings_page = load_ui_file("settings.ui")
        settings.load_settings()

        self.connect_settings_btns()
        self.tabs.addTab(self.settings_page, r"⚙")

        self.setMinimumWidth(settings.get_setting("window_width"))
        self.setMinimumHeight(settings.get_setting("window_height"))

        header = self.settings_page.pb_list.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.settings_page.pb_list.setEditTriggers(QTableWidget.NoEditTriggers)
        self.settings_page.pb_list.cellDoubleClicked.connect(self.__open_from_list)
        self.open_boards()
        self.setCentralWidget(self.tabs)

    def closeEvent(self, event):
        # pylint: disable=invalid-name
        for child in self.findChildren(Page):
            child.save()
            child.close()
        settings.set_setting("window_width", self.width())
        settings.set_setting("window_height", self.height())
        settings.save_settings()
        QMainWindow.closeEvent(self, event)

    def connect_settings_btns(self):
        self.settings_page.btn_add.clicked.connect(self.settings_add_clicked)
        self.settings_page.btn_imp.clicked.connect(self.settings_import_clicked)
        self.settings_page.btn_ren.clicked.connect(self.rename_board)
        self.settings_page.btn_rem.clicked.connect(self.remove_board)

    def settings_add_clicked(self):
        text, ok_clicked = pb_name_dialog(self)
        if ok_clicked:
            n_tabs = self.tabs.count()
            name = text if text else f"New PB{n_tabs}"

            filename = convert_str_to_filename(name)
            filename = os.path.join(settings.get_setting("data_dir"), filename)
            if os.path.exists(filename) and os.path.isfile(filename):
                raise ValueError(f"Projectboard {name} already exists at {filename}!")
            board = f"{filename}:{name}:open"
            self.__append_to_pb_list(board, n_tabs - 1)
            settings.append_to_setting("boards", board)
            self.__add_board(name, filename, n_tabs)

    def settings_import_clicked(self):
        filenames = QFileDialog.getOpenFileNames(
            self, "Open ProjectBoard", settings.get_setting("data_dir"), "PB2 (*.json)"
        )
        filenames = filenames[0]
        if filenames:
            rows = self.settings_page.pb_list.rowCount()
            for filename in filenames:
                metadata = read_metadata(filename)
                name = metadata["name"]
                board = f"{filename}:{name}:closed"
                self.__append_to_pb_list(board, rows)
                settings.append_to_setting("boards", board)
                rows += 1

    def open_boards(self):
        boards = settings.get_setting("boards")
        for i, board in enumerate(boards):
            self.__append_to_pb_list(board, i)
            filename, name, state = board.split(":")
            if state == "open":
                n_tabs = self.tabs.count()
                self.__add_board(name, filename, n_tabs)
        self.tabs.setCurrentIndex(0)

    def rename_board(self, name: Optional[str] = None, filename: Optional[str] = None):
        if name is None and filename is None:
            row = self.settings_page.pb_list.currentRow()
            item = self.settings_page.pb_list.item(row, 0)
            filename, name, _ = item.text().split(":")
        assert name is not None
        assert filename is not None
        text, ok_clicked = pb_name_dialog(self, "Rename Projectboard")
        if ok_clicked:
            boards = settings.get_setting("boards")
            idx: List[int] = [idx for idx, board in enumerate(boards) if board.startswith(filename)]
            assert len(idx) == 1
            idx: int = idx[0]
            board = boards[idx].split(":")
            board[1] = text
            board = ":".join(board)
            boards[idx] = board
            self.settings_page.pb_list.setItem(idx, 0, QTableWidgetItem(board))
            settings.set_setting("boards", boards)
            if board.endswith(":open"):
                boards_open = [board for board in boards if board.endswith(":open")]
                idx = boards_open.index(board)
                wid = self.tabs.widget(idx + 1)
                wid.projectboard.set_metadata({"name": text})
            else:
                pboard = Projectboard("", filename)
                pboard.set_metadata({"name": text})
                pboard.save()
                pboard.close()

            self.tabs.setTabText(idx + 1, text)

    def remove_board(self):
        row = self.settings_page.pb_list.currentRow()
        if row == -1:
            return
        item = self.settings_page.pb_list.item(row, 0)
        item_text = item.text()
        filename, name, state = item_text.split(":")

        title = "Confirm removing!"
        msg = "Remove projectboard board from list: "
        inf_txt = "Attention: this only removes the board from the list. No files are deleted!"

        resp = confirm_del_dialog(self, name, title=title, msg=msg, inf_txt=inf_txt)
        if resp == QMessageBox.Ok:
            boards = settings.get_setting("boards")
            if state == "open":
                cls_idx = [
                    idx
                    for idx, board in enumerate(boards)
                    if board.startswith(filename) and board.endswith(":open")
                ]

                cls_idx = cls_idx[0] + 1
                assert cls_idx > 0
                self.tabs.removeTab(cls_idx)
            boards.remove(item_text)
            self.settings_page.pb_list.removeRow(row)
            settings.set_setting("boards", boards)

    def __add_board(self, name: str, filename: str, n_tabs: int):
        new_tab = Page(name, filename)
        new_tab.widget.btn_close.clicked.connect(new_tab.close)
        new_tab.widget.btn_close.clicked.connect(partial(self.__close_board, new_tab))
        new_tab.widget.btn_ren.clicked.connect(partial(self.rename_board, name, filename))
        self.tabs.insertTab(n_tabs, new_tab, name)
        self.tabs.setCurrentIndex(n_tabs)

    def __close_board(self, new_tab: QWidget):
        idx = self.tabs.indexOf(new_tab)
        filename = new_tab.projectboard.get_filename()
        boards = settings.get_setting("boards")
        board_idx = [i for i, board in enumerate(boards) if board.startswith(filename)]
        assert len(board_idx) == 1
        board_idx = board_idx[0]
        board = boards[board_idx]
        board_item = self.settings_page.pb_list.takeItem(board_idx, 0)
        board = board_item.text()

        boards.remove(board)
        board = board.replace("open", "closed")
        boards.insert(board_idx, board)
        settings.set_setting("boards", boards)
        settings.save_settings()
        board_item.setText(board)
        self.settings_page.pb_list.setItem(board_idx, 0, board_item)

        self.tabs.removeTab(idx)
        del new_tab
        self.tabs.setCurrentIndex(0)

    def __append_to_pb_list(self, board: str, row: int):
        self.settings_page.pb_list.insertRow(row)
        self.settings_page.pb_list.setItem(row, 0, QTableWidgetItem(board))

    def __open_from_list(self, row, column):

        board_item = self.settings_page.pb_list.takeItem(row, column)
        board = board_item.text()
        boards = settings.get_setting("boards")

        if board.endswith(":closed"):
            _ = boards.pop(row)
            board = board.replace("closed", "open")
            boards.insert(row, board)
            settings.set_setting("boards", boards)
            board_item.setText(board)

            filename, name, _state = board.split(":")
            boards_open = [b for b in boards if b.endswith(":open")]
            idx = boards_open.index(board)
            self.__add_board(name, filename, idx + 1)
        else:
            boards_open = [b for b in boards if b.endswith(":open")]
            idx = boards_open.index(board)
            self.tabs.setCurrentIndex(idx + 1)
        self.settings_page.pb_list.setItem(row, column, board_item)


class Page(QStackedWidget):
    def __init__(self, name: str, filename: str):
        super().__init__()
        self.widget = load_ui_file("projectboard_horizontal.ui", self)
        self.projectboard = Projectboard(name, filename)

        self.ui_state = StateInt(
            0,
            [-1, 0, 1, 2, 3],
            ["Project plan", "Projectboard", "Project", "Milestone", "Task"],
        )

        project_list = self.projectboard.get_project_order()
        project_list = project_list["project_order"]
        self.widget.list_projects.setRowCount(len(project_list))
        for i_p, pid in enumerate(project_list):
            data = self.projectboard.get(pid)
            self.__add_project_to_list(data, i_p)

        self.widget.setCurrentIndex(0)
        self.__hide_tm_fields()
        self.widget.show()

        self.widget.btn_save.clicked.connect(self.save)
        self.widget.btn_add.clicked.connect(partial(self.widget.setCurrentIndex, 1))
        self.widget.btn_add.clicked.connect(partial(setattr, self.ui_state, "state", 1))
        self.widget.btn_add.clicked.connect(partial(self.set_data, data=None, parent_id=""))
        self.widget.btn_add.clicked.connect(self.__set_buttons)

        self.widget.btn_add_M.clicked.connect(partial(self.add_milestone, None))
        self.widget.btn_add_T.clicked.connect(partial(self.add_task, None))
        self.widget.btn_apply.clicked.connect(self.apply_clicked)
        self.widget.le_name.returnPressed.connect(self.apply_clicked)

        self.widget.btn_del.clicked.connect(self.del_proj)

        self.states = self.projectboard.get("custom_states")
        if self.states is None:
            self.states = settings.get_setting("default_states")
            states: Dict[str, Optional[str]] = {}
            states["id"] = "custom_states"
            states["category"] = None
            states["states"] = self.states
            self.projectboard.insert(states)
        else:
            self.states = self.states["states"]
        self.widget.cb_states.addItems(self.states)

        self.__set_list_headers()

        self.widget.list_projects.setColumnHidden(0, True)
        self.widget.list_projects.cellDoubleClicked.connect(self.cell_clicked)

        self.widget.list_tasks.setColumnHidden(1, True)
        self.widget.list_tasks.itemDoubleClicked.connect(self.__connect_item)

        # self.widget.le_id.setHidden(True)
        # self.widget.le_parent_id.setHidden(True)

        self.widget.btn_pp.setHidden(True)
        # self.widget.btn_pp.clicked.connect(self.project_plan)
        # self.widget.btn_pp_close.clicked.connect(self.widget.project_plan.clear())
        self.widget.btn_pp_close.clicked.connect(partial(self.widget.setCurrentIndex, 0))
        self.widget.btn_exp.setHidden(True)

    def __set_list_headers(self):
        header = self.widget.list_projects.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)

        header = self.widget.list_tasks.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

    def __set_buttons(self):
        if self.ui_state <= 0:
            return

        set_m_btn, set_t_btn = True, True
        match self.ui_state.state:
            case 1:
                set_m_btn, set_t_btn = False, True
                label_cat = "Project"
                label_tm = "Milestones and Tasks"
                set_tm_hidden = False
            case 2:
                set_m_btn, set_t_btn = True, False
                label_cat = "Milestone"
                label_tm = "Tasks"
                set_tm_hidden = False
            case 3:
                set_m_btn, set_t_btn = True, True
                label_cat = "Task"
                label_tm = ""
                set_tm_hidden = True
            case _:
                raise NotImplementedError

        self.widget.btn_add_M.setHidden(set_m_btn)
        self.widget.btn_add_T.setHidden(set_t_btn)
        self.widget.label_cat.setText(label_cat)
        self.widget.label_tm.setText(label_tm)
        self.widget.label_tm.setHidden(set_tm_hidden)
        self.widget.list_tasks.setHidden(set_tm_hidden)

    def set_data(self, data: dict | None, parent_id: Optional[str] = None):
        self.__clear()

        if data is None:
            self.widget.le_id.setText(generate_id())
        else:
            self.widget.le_name.setText(data["name"])
            self.widget.te_desc.setMarkdown(data["description"])
            self.widget.cb_states.setCurrentIndex(self.states.index(data["state"]))
            self.widget.le_id.setText(data["id"])
            parent_id = data["parent"]
            children = self.projectboard.get_children(data["id"])
            if children:
                self.__fill_task_list(children)

            if self.ui_state > 1:
                parent = self.projectboard.get(parent_id)
                min_date = QtCore.QDate.fromString(parent["startdate"])
                max_date = QtCore.QDate.fromString(parent["duedate"])
                self.widget.date_start.setDateRange(min_date, max_date)
                self.widget.date_due.setDateRange(min_date, max_date)
            else:
                min_date = QtCore.QDate(2000, 1, 1)
                max_date = QtCore.QDate(2200, 12, 31)
                self.widget.date_start.setDateRange(min_date, max_date)
                self.widget.date_due.setDateRange(min_date, max_date)

            duedate = QtCore.QDate.fromString(data["duedate"])
            startdate = QtCore.QDate.fromString(data["startdate"])
            self.widget.date_start.setDate(startdate)
            self.widget.date_due.setDate(duedate)

        assert parent_id is not None
        self.widget.le_parent_id.setText(parent_id)

    def get_data(self) -> dict:
        data = {}
        data["name"] = self.widget.le_name.text()
        data["description"] = self.widget.te_desc.toMarkdown()
        data["duedate"] = self.widget.date_due.date().toString()
        data["startdate"] = self.widget.date_start.date().toString()
        data["state"] = self.widget.cb_states.currentText()
        data["parent"] = self.widget.le_parent_id.text()
        data["id"] = self.widget.le_id.text()
        data["category"] = self.ui_state.get_current_state_name().lower()
        return data

    def cell_clicked(self, row, _):
        cell_id = self.widget.list_projects.item(row, 0).text()
        data = self.projectboard.get(cell_id)
        self.set_data(data)
        self.ui_state.state = 1
        self.__set_buttons()
        self.widget.setCurrentIndex(1)

    def apply_clicked(self):
        data = self.get_data()

        match data["category"].lower():
            case "project":
                self.projectboard.insert(data)
                self.ui_state.state = 0
                self.widget.setCurrentIndex(0)
                if self.widget.list_projects.findItems(data["id"], Qt.MatchExactly):
                    rows = self.widget.list_projects.currentRow()
                    self.widget.list_projects.removeRow(rows)
                    self.widget.list_projects.insertRow(rows)
                else:
                    rows = self.widget.list_projects.rowCount()
                    self.widget.list_projects.setRowCount(rows + 1)
                self.widget.list_projects.setCurrentCell(rows, 1)
                self.__add_project_to_list(data, rows)
            case "milestone":
                self.ui_state.state = 1
                parent = self.projectboard.get(data["parent"])
                self.projectboard.insert_sub_item(data, parent)
                self.set_data(parent)
            case "task":
                diff = self.ui_state.state - self.ui_state.prev_state
                if diff < 1 or diff > 2:
                    raise NotImplementedError

                self.ui_state.state = self.ui_state.prev_state
                parent = self.projectboard.get(data["parent"])
                assert parent is not None
                self.projectboard.insert_sub_item(data, parent)
                if diff == 2:
                    parent = self.projectboard.get(parent["parent"])
                self.set_data(parent)
        self.__set_buttons()

    def add_milestone(self, item_id: Optional[str] = None):
        data = None
        parent_id = None

        if item_id is not None:
            data = self.projectboard.get(item_id)
        else:
            parent = self.get_data()
            parent_id = parent["id"]
            self.projectboard.insert(parent)

        self.ui_state.state = 2
        self.__set_buttons()
        self.set_data(data, parent_id)

    def add_task(self, item_id: Optional[str] = None):
        data = None
        parent_id = None

        if item_id is not None:
            data = self.projectboard.get(item_id)
        else:
            parent = self.get_data()
            parent_id = parent["id"]
            grandparent_id = parent["parent"]
            grandparent = self.projectboard.get(grandparent_id)
            self.projectboard.insert_sub_item(parent, grandparent)

        self.ui_state.state = 3
        self.__set_buttons()
        self.set_data(data, parent_id)

    def del_proj(self):
        _id = self.widget.le_id.text()
        parent_id = self.widget.le_parent_id.text()
        item = self.get_data()
        resp = confirm_del_dialog(self, f"{item['category']}: {item['name']}")
        if resp == QMessageBox.Ok:
            self.projectboard.delete_subelements(_id, True)

            match self.ui_state.state:
                case 1:
                    self.ui_state.state = 0
                    self.widget.setCurrentIndex(0)
                    self.__clear()
                    if self.widget.list_projects.findItems(_id, Qt.MatchExactly):
                        rows = self.widget.list_projects.currentRow()
                        self.widget.list_projects.removeRow(rows)
                case 2:
                    self.ui_state.state = 1
                    data = self.projectboard.get(parent_id)
                    self.set_data(data)
                case 3:
                    diff = self.ui_state.state - self.ui_state.prev_state
                    if diff < 1 or diff > 2:
                        raise NotImplementedError

                    self.ui_state.state = self.ui_state.prev_state
                    data = self.projectboard.get(parent_id)
                    assert data is not None
                    if diff == 2:
                        data = self.projectboard.get(data["parent"])
                    self.set_data(data)
                case _:
                    raise NotImplementedError
            self.__set_buttons()

    def project_plan(self):
        metadata = self.projectboard.get_metadata()
        self.widget.label_pp.setText(f"Project plan: {metadata['name']}")
        self.widget.setCurrentIndex(2)

    def save(self):
        self.projectboard.save()

    def close(self):
        self.projectboard.close()

    def __hide_tm_fields(self, hide: bool = True):
        self.widget.label_type.setHidden(hide)
        self.widget.cb_type.setHidden(hide)
        self.widget.label_belongs.setHidden(hide)
        self.widget.cb_belongs.setHidden(hide)

    def __clear(self):
        self.widget.le_id.clear()
        self.widget.le_parent_id.clear()
        self.widget.le_name.clear()
        self.widget.te_desc.clear()
        today = QtCore.QDate.currentDate()
        self.widget.date_start.setDate(today)
        self.widget.date_due.setDate(today.addMonths(1))
        self.widget.cb_states.setCurrentIndex(0)
        self.widget.list_tasks.clear()

    def __add_project_to_list(self, data: dict, row: int):

        (
            n_ms,
            n_ms_finished,
            n_tasks,
            n_tasks_finished,
        ) = self.projectboard.number_milestones_and_tasks(data["id"])

        cols = [
            QTableWidgetItem(data["id"]),
            QTableWidgetItem(data["name"]),
            QTableWidgetItem(data["state"]),
            QTableWidgetItem(f"{n_ms}"),
            QTableWidgetItem(f"{n_ms_finished}"),
            QTableWidgetItem(f"{n_tasks}"),
            QTableWidgetItem(f"{n_tasks_finished}"),
            QTableWidgetItem(data["startdate"]),
            QTableWidgetItem(data["duedate"]),
        ]

        for i_col, col in enumerate(cols[1:], start=1):
            self.widget.list_projects.setItem(row, i_col, col)

        self.widget.list_projects.setItem(row, 0, cols[0])

    def __fill_task_list(self, data: List[Dict[str, str]], parent: QTreeWidgetItem | None = None):

        for item in data:
            item_id = item["id"]
            type_ = item["category"].capitalize()
            name = item["name"]
            state = item["state"]
            startdate = item["startdate"]
            duedate = item["duedate"]
            entry = [type_[0], item_id, name, state, startdate, duedate]
            wid = QTreeWidgetItem(parent, entry)

            if type_ == "Milestone" and (children := self.projectboard.get_children(item_id)):
                self.__fill_task_list(children, wid)

            if parent is None:
                self.widget.list_tasks.addTopLevelItem(wid)
                self.widget.list_tasks.expandItem(wid)
            else:
                parent.addChild(wid)

    def __connect_item(self, item):
        item_id = item.text(1)
        item_cat = item.text(0)
        match item_cat:
            case "M":
                self.add_milestone(item_id)
            case "T":
                self.add_task(item_id)
            case _:
                raise NotImplementedError


def load_ui_file(filename, parent=None) -> QWidget:
    loader = QtUiTools.QUiLoader()
    file_path = os.path.dirname(__file__)
    ui_fn = os.path.join(file_path, filename)
    uifile = QtCore.QFile(ui_fn)
    uifile.open(QtCore.QFile.ReadOnly)
    gui = loader.load(uifile, parent)
    uifile.close()
    return gui


def pb_name_dialog(parent: QWidget, title: str = "New Projectboard") -> tuple[str, str]:
    return QInputDialog.getText(parent, title, "Enter name:", QLineEdit.Normal)


def convert_str_to_filename(
    name: str, directory: str = "~/Documents/pyprojectboards", extension: str = ".json"
) -> str:
    keep_chars = (".", "_")
    filename = "".join(char for char in name if char.isalnum() or char in keep_chars)

    if not filename.endswith(extension):
        filename += extension

    directory = os.path.expanduser(directory)
    return os.path.join(directory, filename)


def confirm_del_dialog(
    parent: QWidget,
    item_name: str,
    title: Optional[str] = None,
    msg: Optional[str] = None,
    inf_txt: Optional[str] = None,
) -> int:
    if title is None:
        title = "Please confirm deletion!"
    if msg is None:
        msg = "Do you really want to delete "
    if inf_txt is None:
        inf_txt = "Attention: sub-items (such milestones, tasks, ...) will also be deleted!"
    msg += f"{item_name}?"

    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(msg)
    dialog.setInformativeText(inf_txt)
    dialog.setIcon(QMessageBox.Warning)
    dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    dialog.setDefaultButton(QMessageBox.Cancel)
    return dialog.exec()
