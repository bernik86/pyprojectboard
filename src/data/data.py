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
from datetime import datetime
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

# pylint: disable=import-error
from tinydb import Query
from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
from tinydb.storages import MemoryStorage

from data import defaults  # type: ignore

# pylint: enable=import-error


cat_values = {
    "project": 1,
    "milestone": 2,
    "task": 3,
}


class Projectboard:
    def __init__(self, name: str, filename: str, db_in_memory: bool = False):
        self.__name__ = name
        self.__filename__ = filename
        if db_in_memory:
            self.__database__ = TinyDB(storage=MemoryStorage)
        else:
            dirname = os.path.dirname(filename)
            os.makedirs(dirname, exist_ok=True)
            self.__database__ = TinyDB(filename, storage=CachingMiddleware(JSONStorage))

        query = Query()
        metadata = self.__database__.get(query.metadata.exists())

        if metadata is None:
            metadata = {
                "metadata": {
                    "filename": self.__filename__,
                    "name": self.__name__,
                    "description": "",
                }
            }
            self.__database__.insert(metadata)
        elif not self.__name__:
            self.__name__ = metadata["metadata"]["name"]

        project_order = self.__database__.get(query.project_order.exists())
        if project_order is None:
            self.__database__.insert({"project_order": []})

    def close(self):
        self.__database__.close()

    def insert(self, data: dict):
        assert "id" in data
        assert "category" in data

        query_item = Query()

        if data["category"] == "project":
            p_order = self.get_project_order()

            if data["id"] not in p_order["project_order"]:
                p_order["project_order"].append(data["id"])
                p_order_query = query_item.project_order.exists()
                self.__database__.upsert(p_order, p_order_query)

        self.__database__.upsert(data, query_item.id == data["id"])

    def get(self, item_id: str) -> Optional[dict[str, Any]]:
        query = Query()
        n_items = self.__database__.count(query.id == item_id)
        if n_items == 0:
            return None
        if n_items > 1:
            raise ValueError("Too many entries with same id in database!")

        return self.__database__.get(query.id == item_id)

    def insert_sub_item(self, sub_item: dict, parent: dict):
        cat_value_sub_item = cat_values[sub_item["category"]]
        cat_value_parent = cat_values[parent["category"]]

        if cat_value_parent >= cat_value_sub_item:
            raise ValueError
        if sub_item["parent"] is None:
            sub_item["parent"] = parent["id"]
            parent["sub_items"].append(sub_item["id"])

        self.insert(sub_item)
        self.insert(parent)

    def delete(self, item_id: str):
        query = Query()

        parent = self.__database__.search(query.sub_items.any(item_id))
        for par in parent:
            par["sub_items"].remove(item_id)
            self.insert(par)

        projects = self.__database__.search(query.project_order.any(item_id))
        if projects:
            projects[0]["project_order"].remove(item_id)
            self.set_project_order(projects[0])

        self.__database__.remove(query.id == item_id)

    def delete_subelements(self, item_id: str, delete_item: bool = False):
        """Deletes all sub items and their sub items recursively"""
        query = Query()
        children = self.__database__.search(query.parent == item_id)

        for child in children:
            self.delete_subelements(child["id"], True)

        if delete_item:
            self.delete(item_id)

    def get_project_order(self) -> dict:
        query_item = Query()
        p_order_query = query_item.project_order.exists()
        p_order = self.__database__.get(p_order_query)
        return p_order

    def set_project_order(self, project_order: dict):
        query_item = Query()
        p_order_query = query_item.project_order.exists()
        self.__database__.upsert(project_order, p_order_query)

    def move_item_by(self, item_id: str, n_pos: int, mv_sub_item: bool = False):
        if mv_sub_item:
            self.__move_subitem(item_id, n_pos)
        else:
            self.__move_project(item_id, n_pos)

    def __move_project(self, item_id: str, n_pos: int):
        project_order = self.get_project_order()
        move_item_in_list_by_n(item_id, project_order["project_order"], n_pos)
        self.set_project_order(project_order)

    def __move_subitem(self, sub_item_id: str, n_pos: int):
        sub_item = self.get(sub_item_id)
        if sub_item is None:
            raise KeyError(f"Sub-item ({sub_item_id}) does not exist!")

        parent_id = sub_item["parent"]
        parent = self.get(parent_id)
        if parent is None:
            raise KeyError(f"Parent item ({parent_id}) does not exist!")

        parent_items = parent["sub_items"]
        move_item_in_list_by_n(sub_item_id, parent_items, n_pos)
        self.insert(parent)

    def save(self):
        if isinstance(self.__database__.storage, CachingMiddleware):
            self.__database__.storage.flush()

    def set_metadata(self, metadata: dict[str, str]):
        stored_metadata = self.get_metadata()
        stored_metadata.update(metadata)
        self.__database__.upsert({"metadata": stored_metadata}, Query().metadata.exists())

    def get_metadata(self) -> dict[str, str]:
        metadata = self.__database__.get(Query().metadata.exists())
        return metadata["metadata"]

    def get_filename(self) -> str:
        return self.__filename__

    def set_states(self, states: list[str]):
        raise NotImplementedError

    def get_states(self) -> list[str] | None:
        raise NotImplementedError

    def number_milestones_and_tasks(self, pid: str) -> Tuple[int, int, int, int]:
        """Returns (n_milestones, n_milestones_achieved, n_tasks, n_tasks_finished)"""
        states = self.get("custom_states")
        if states is None:
            state_finished = defaults.DEFAULT_STATES[-1]
        else:
            state_finished = states["states"][-1]

        n_ms = 0
        n_ms_finished = 0
        n_tasks = 0
        n_tasks_finished = 0

        result = self.__milestones_and_tasks(pid, state_finished)
        n_ms += result[0]
        n_ms_finished += result[1]
        n_tasks += result[2]
        n_tasks_finished += result[3]

        return (n_ms, n_ms_finished, n_tasks, n_tasks_finished)

    def __milestones_and_tasks(
        self, item_id: str, state_finished: str
    ) -> Tuple[int, int, int, int]:
        children = self.get_children(item_id)
        item = self.get(item_id)

        if item is None:
            raise ValueError(f"Item with id {item_id} does not exist!")

        n_ms = 0
        n_ms_finished = 0
        n_tasks = 0
        n_tasks_finished = 0

        for child in children:
            result = self.__milestones_and_tasks(child["id"], state_finished)
            n_ms += result[0]
            n_ms_finished += result[1]
            n_tasks += result[2]
            n_tasks_finished += result[3]

        cat = item["category"]
        finished = item["state"] == state_finished
        if cat == "milestone":
            n_ms += 1
            n_ms_finished += int(finished)
        elif cat == "task":
            n_tasks += 1
            n_tasks_finished += int(finished)
        elif cat == "project":
            pass
        else:
            raise NotImplementedError

        return (n_ms, n_ms_finished, n_tasks, n_tasks_finished)

    def get_children(self, item_id: str) -> list[dict[str, Any]]:
        query = Query()
        return self.__database__.search(query.parent == item_id)

    def is_child_of(self, child_id: str, parent_id: str) -> bool:
        children = self.get_children(parent_id)
        for child in children:
            if child["id"] == child_id:
                return True
        return False

    def n_children(self, item_id: str) -> int:
        query = Query()
        n_child = len(self.__database__.search(query.parent == item_id))
        return n_child

    def __repr__(self) -> str:
        rep = []
        for elem in self.__database__.all():
            rep.append(repr(elem))

        return "\n".join(rep)


def create_default_item(can_have_subitems: bool = True) -> dict[str, Any]:
    today = datetime.today().date().isoformat()
    item: dict[str, Any] = {
        "name": "default project",
        "id": generate_id(),
        "category": "project",
        "description": "new default project",
        "startdate": today,
        "duedate": today,
        "state": "Open",
        "parent": None,
    }
    if can_have_subitems:
        item["sub_items"] = []

    return item


def generate_id(time: datetime | None = None) -> str:
    """Function to create ID based on current time."""
    time = datetime.now() if time is None else time
    return str(time).replace(" ", "-")


def move_item_in_list_by_n(item: str, list_of_str: List[str], n_pos: int):
    assert item in list_of_str
    old_idx = list_of_str.index(item)
    new_idx = old_idx + n_pos
    new_idx = new_idx if new_idx >= 0 else 0
    list_of_str.insert(new_idx, list_of_str.pop(old_idx))


def read_metadata(filename: str) -> dict[str, str]:
    board = Projectboard("", filename)
    metadata = board.get_metadata()
    board.close()
    del board
    return metadata
