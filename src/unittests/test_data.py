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
import random
import unittest
from datetime import datetime

# pylint: disable=import-error
from tinydb import Query
from tinydb import TinyDB

from data.data import Projectboard  # type: ignore
from data.data import create_default_item
from data.data import generate_id
from data.data import move_item_in_list_by_n
from data.data import read_metadata

# pylint: enable=import-error


FILENAME_TEST_DB = "test_db.json"


class TestProjectboardBasicDatabaseActions(unittest.TestCase):
    def setUp(self):
        self.pboard = Projectboard("Test", FILENAME_TEST_DB, db_in_memory=True)
        self.item = create_default_item()
        self.item["id"] = "2023-12-08-16:19:16.781414"
        self.n_proj = None

    def test_1_init(self):
        metadata = self.pboard.__database__.get(Query().metadata.exists())["metadata"]
        project_order = self.pboard.__database__.get(Query().project_order.exists())

        self.assertEqual(self.pboard.__name__, "Test")
        self.assertEqual(self.pboard.__filename__, FILENAME_TEST_DB)
        self.assertTrue(isinstance(self.pboard.__database__, TinyDB))
        self.assertEqual(metadata["name"], "Test")
        self.assertEqual(metadata["filename"], FILENAME_TEST_DB)
        self.assertNotEqual(project_order, None)

    def test_2_insert(self):
        self.pboard.insert(self.item)
        query = Query()
        item = self.pboard.__database__.get(query.id == self.item["id"])
        self.assertEqual(item, self.item)
        p_order_query = query.project_order.exists()
        p_order = self.pboard.__database__.get(p_order_query)
        self.assertEqual(p_order["project_order"][-1], self.item["id"])

    def test_3_get_item(self):
        self.pboard.insert(self.item)
        self.pboard.__database__.insert(self.item)

        with self.assertRaises(ValueError):
            _ = self.pboard.get(self.item["id"])

        query = Query()
        self.pboard.__database__.remove(query.id == self.item["id"])

        self.pboard.insert(self.item)
        result = self.pboard.get(self.item["id"])
        self.assertEqual(self.item, result)

        result = self.pboard.get("42")
        self.assertEqual(None, result)

    def test_4_close_database(self):
        self.pboard.close()
        try:
            self.pboard.insert({"name": "test", "id": 42, "category": "task"})
        except ValueError:
            pass

    def test_5_delete_item(self):
        self.n_proj = 10
        for i in range(self.n_proj):
            self.item = create_default_item()
            self.item["id"] = f"P{i}"
            self.item["name"] = f"P{i}"
            self.pboard.insert(self.item)

        self.assertEqual(12, len(self.pboard.__database__.all()))

        self.pboard.delete("P4")
        self.assertEqual(None, self.pboard.get("P4"))
        self.assertEqual(11, len(self.pboard.__database__.all()))

        self.pboard.delete("P8")
        self.assertEqual(None, self.pboard.get("P8"))
        self.assertEqual(10, len(self.pboard.__database__.all()))

    def test_6_get_metadta(self):
        metadata = self.pboard.get_metadata()
        self.assertEqual(metadata["name"], "Test")
        self.assertEqual(metadata["filename"], FILENAME_TEST_DB)
        self.assertEqual(metadata["description"], "")

    def test_7_set_metadata(self):
        desc_str = "Test PB 1"
        desc = {"description": desc_str}
        self.pboard.set_metadata(desc)
        metadata = self.pboard.__database__.get(Query().metadata.exists())["metadata"]
        self.assertEqual(metadata["name"], "Test")
        self.assertEqual(metadata["filename"], FILENAME_TEST_DB)
        self.assertEqual(metadata["description"], desc_str)

    def tearDown(self):
        try:
            self.pboard.__database__.close()
        except ValueError:
            pass


class TestProjectboardInsertSubItems(unittest.TestCase):
    def setUp(self):
        self.pboard = Projectboard("Test", FILENAME_TEST_DB, db_in_memory=True)
        self.item = create_default_item()
        self.item["id"] = "2023-12-08-16:19:16.781414"
        self.pboard.insert(self.item)

    def test_1_add_milestone_to_project(self):
        # Add Milestone to Project
        sub_item = create_default_item()
        sub_item["category"] = "milestone"
        sub_item["id"] = "M1"
        self.pboard.insert_sub_item(sub_item, self.item)

        updated_item = self.pboard.get(self.item["id"])
        self.assertEqual(sub_item["id"], updated_item["sub_items"][0])

        self.assertEqual(self.pboard.n_children(self.item["id"]), 1)
        self.assertEqual(self.pboard.get_children(self.item["id"])[0], sub_item)
        self.assertTrue(self.pboard.is_child_of(sub_item["id"], self.item["id"]))

    def test_2_add_task_to_milestone(self):
        sub_item = create_default_item()
        sub_item["category"] = "milestone"
        sub_item["id"] = "M1"
        self.pboard.insert_sub_item(sub_item, self.item)
        updated_item = self.pboard.get(sub_item["id"])
        self.assertEqual(updated_item["parent"], self.item["id"])

        # Add Task to Milestone
        sub_item = create_default_item()
        sub_item["category"] = "task"
        sub_item["id"] = "T1"
        parent_item = self.pboard.get("M1")
        self.pboard.insert_sub_item(sub_item, parent_item)
        updated_item = self.pboard.get(parent_item["id"])

        self.assertEqual(sub_item["id"], updated_item["sub_items"][0])

        self.assertEqual(sub_item, self.pboard.get_children(parent_item["id"])[0])
        self.assertEqual(self.pboard.n_children(parent_item["id"]), 1)
        self.assertTrue(self.pboard.is_child_of(sub_item["id"], parent_item["id"]))

    def test_3_add_task_to_project(self):
        # Add Task to Project
        sub_item = create_default_item()
        sub_item["category"] = "task"
        sub_item["id"] = "T2"
        parent_item = self.pboard.get(self.item["id"])
        self.pboard.insert_sub_item(sub_item, parent_item)
        updated_item = self.pboard.get(parent_item["id"])

        self.assertEqual(sub_item["id"], updated_item["sub_items"][-1])

        self.assertEqual(sub_item, self.pboard.get_children(parent_item["id"])[0])
        self.assertEqual(self.pboard.n_children(parent_item["id"]), 1)
        self.assertTrue(self.pboard.is_child_of(sub_item["id"], parent_item["id"]))

    def test_4_add_milestone_to_task(self):
        """This test should fail"""
        sub_item = create_default_item()
        sub_item["category"] = "task"
        sub_item["id"] = "T1"
        self.pboard.insert_sub_item(sub_item, self.item)

        sub_item = create_default_item()
        sub_item["category"] = "milestone"
        sub_item["id"] = "M2"
        parent_item = self.pboard.get("T1")
        with self.assertRaises(ValueError):
            self.pboard.insert_sub_item(sub_item, parent_item)

    def test_5_add_project_to_project(self):
        """This test should fail"""
        sub_item = create_default_item()
        parent_item = self.pboard.get(self.item["id"])
        with self.assertRaises(ValueError):
            self.pboard.insert_sub_item(sub_item, parent_item)

    def test_6_add_project_to_task(self):
        """This test should fail"""
        sub_item = create_default_item()
        sub_item["category"] = "task"
        sub_item["id"] = "T1"
        self.pboard.insert_sub_item(sub_item, self.item)

        sub_item = create_default_item()
        parent_item = self.pboard.get("T1")
        with self.assertRaises(ValueError):
            self.pboard.insert_sub_item(sub_item, parent_item)

    def test_7_add_project_to_milestone(self):
        """This test should fail"""
        sub_item = create_default_item()
        sub_item["category"] = "milestone"
        sub_item["id"] = "M1"
        self.pboard.insert_sub_item(sub_item, self.item)

        sub_item = create_default_item()
        parent_item = self.pboard.get("M1")
        with self.assertRaises(ValueError):
            self.pboard.insert_sub_item(sub_item, parent_item)

    def test_8_custom_states(self):
        states = self.pboard.get("custom_states")
        self.assertEqual(states, None)

        custom_states = ["Open", "WIP", "Closed"]
        states = {
            "id": "custom_states",
            "category": None,
            "states": custom_states,
        }
        self.pboard.insert(states)

        states = self.pboard.get("custom_states")
        self.assertEqual(custom_states, states["states"])

    def test_9_number_mt(self):
        custom_states = ["Open", "WIP", "Closed"]
        states = {
            "id": "custom_states",
            "category": None,
            "states": custom_states,
        }
        self.pboard.insert(states)

        n_m = random.randint(1, 10)
        n_m_finished = 0
        n_t_t = 0
        n_t_finished = 0
        for i in range(n_m):
            sub_item = create_default_item()
            sub_item["category"] = "milestone"
            sub_item["id"] = f"M{i}"
            if i == random.randint(1, 10) > 3:
                sub_item["state"] = "Closed"
                n_m_finished += 1
            self.pboard.insert_sub_item(sub_item, self.item)

            n_t = random.randint(1, 5)
            n_t_t += n_t
            for j in range(n_t):
                task_item = create_default_item()
                task_item["category"] = "task"
                task_item["id"] = f"T{i}{j}"
                if j == random.randint(1, 10) > 3:
                    task_item["state"] = "Closed"
                    n_t_finished += 1

                self.pboard.insert_sub_item(task_item, sub_item)

        results = self.pboard.number_milestones_and_tasks(self.item["id"])
        self.assertEqual((n_m, n_m_finished, n_t_t, n_t_finished), results)

    def test_10_get_number_of_children(self):
        n_m = random.randint(1, 10)
        for i in range(n_m):
            sub_item = create_default_item()
            sub_item["category"] = "milestone"
            sub_item["id"] = f"M{i}"
            self.pboard.insert_sub_item(sub_item, self.item)

            if i == 0:
                first_ms_id = sub_item["id"]
                n_t = random.randint(1, 5)

                for j in range(n_t):
                    task_item = create_default_item()
                    task_item["category"] = "task"
                    task_item["id"] = f"T{i}{j}"
                    self.pboard.insert_sub_item(task_item, sub_item)

        self.assertEqual(self.pboard.n_children(self.item["id"]), n_m)
        self.assertEqual(self.pboard.n_children(first_ms_id), n_t)

    def tearDown(self):
        self.pboard.__database__.close()


class TestProjectboardDeleteSubItems(unittest.TestCase):
    def setUp(self):
        self.pboard = Projectboard("Test", FILENAME_TEST_DB, db_in_memory=True)
        self.item = create_default_item()
        self.item["id"] = "2023-12-08-16:19:16.781414"
        self.pboard.insert(self.item)

        for i in range(2):
            sub_item = create_default_item()
            sub_item["category"] = "milestone"
            sub_item["id"] = f"M{i}"
            self.pboard.insert_sub_item(sub_item, self.item)

            for j in range(2):
                task_item = create_default_item()
                task_item["category"] = "task"
                task_item["id"] = f"T{i}{j}"
                self.pboard.insert_sub_item(task_item, sub_item)

    def test_1_delete_task_and_milestone(self):
        self.pboard.delete("T01")
        self.assertEqual(self.pboard.n_children("M0"), 1)
        milestone = self.pboard.get("M0")
        self.assertEqual(milestone["sub_items"], ["T00"])

        self.pboard.delete("M0")
        self.assertEqual(self.pboard.n_children(self.item["id"]), 1)
        updated_item = self.pboard.get(self.item["id"])
        self.assertEqual(updated_item["sub_items"], ["M1"])

        self.pboard.delete("T10")
        self.assertEqual(self.pboard.n_children("M1"), 1)
        milestone = self.pboard.get("M1")
        self.assertEqual(milestone["sub_items"], ["T11"])

    def test_2_delete_all_subitems(self):
        self.pboard.delete_subelements(self.item["id"])
        self.assertEqual(self.pboard.n_children(self.item["id"]), 0)

        updated_item = self.pboard.get(self.item["id"])
        self.assertEqual([], updated_item["sub_items"])

        result = self.pboard.number_milestones_and_tasks(self.item["id"])
        self.assertTrue(not all(result))
        self.assertTrue(not any(result))

    def test_3_delete_all_subitems_and_project(self):

        self.pboard.delete_subelements(self.item["id"], True)
        updated_item = self.pboard.get(self.item["id"])
        self.assertEqual(updated_item, None)

        query = Query()
        self.assertEqual([], self.pboard.__database__.search(query.category == "project"))
        self.assertEqual([], self.pboard.__database__.search(query.category == "task"))
        self.assertEqual([], self.pboard.__database__.search(query.category == "milestone"))
        self.assertEqual([], self.pboard.get_project_order()["project_order"])

    def tearDown(self):
        self.pboard.__database__.close()


class TestProjectboardSortMethods(unittest.TestCase):
    def setUp(self):
        self.pboard = Projectboard("Test", FILENAME_TEST_DB, db_in_memory=True)
        self.n_proj = 10
        for i in range(self.n_proj):
            self.item = create_default_item()
            self.item["id"] = f"P{i}"
            self.item["name"] = f"P{i}"
            self.pboard.insert(self.item)

    def test_1_get_project_order(self):
        order = [f"P{i}" for i in range(self.n_proj)]
        actual_order = self.pboard.get_project_order()
        self.assertEqual(order, actual_order["project_order"])

    def test_2_set_project_order(self):
        order = random.sample(range(self.n_proj), self.n_proj)
        self.pboard.set_project_order({"project_order": order})
        actual_order = self.pboard.get_project_order()
        self.assertEqual(order, actual_order["project_order"])

    def test_3_mv_project(self):
        order = self.pboard.get_project_order()["project_order"]
        for _ in range(500):
            old_idx = random.randint(0, self.n_proj - 1)
            n_pos = random.randint(-5, 5)
            item = order[old_idx]
            self.pboard.move_item_by(item, n_pos)
            order = self.pboard.get_project_order()["project_order"]
            new_idx = old_idx + n_pos
            new_idx = new_idx if new_idx >= 0 else 0
            new_idx = new_idx if new_idx < self.n_proj else self.n_proj - 1
            self.assertEqual(item, order[new_idx])

    def test_4_mv_milestone(self):
        n_miles = 15
        for i in range(n_miles):
            sub_item = create_default_item()
            sub_item["name"] = f"M{i}"
            sub_item["id"] = f"M{i}"
            sub_item["category"] = "milestone"
            self.pboard.insert_sub_item(sub_item, self.item)

        order = self.item["sub_items"]
        for _ in range(500):
            old_idx = random.randint(0, n_miles - 1)
            n_pos = random.randint(-5, 5)
            item = order[old_idx]
            self.pboard.move_item_by(item, n_pos, True)
            updated_item = self.pboard.get(self.item["id"])
            order = updated_item["sub_items"]
            new_idx = old_idx + n_pos
            new_idx = new_idx if new_idx >= 0 else 0
            new_idx = new_idx if new_idx < n_miles else n_miles - 1
            self.assertEqual(item, order[new_idx])

    def test_5_mv_task(self):
        n_tasks = 15
        for i in range(n_tasks):
            sub_item = create_default_item()
            sub_item["name"] = f"T{i}"
            sub_item["id"] = f"T{i}"
            sub_item["category"] = "task"
            self.pboard.insert_sub_item(sub_item, self.item)

        order = self.item["sub_items"]
        for _ in range(500):
            old_idx = random.randint(0, n_tasks - 1)
            n_pos = random.randint(-5, 5)
            item = order[old_idx]
            self.pboard.move_item_by(item, n_pos, True)
            updated_item = self.pboard.get(self.item["id"])
            order = updated_item["sub_items"]
            new_idx = old_idx + n_pos
            new_idx = new_idx if new_idx >= 0 else 0
            new_idx = new_idx if new_idx < n_tasks else n_tasks - 1
            self.assertEqual(item, order[new_idx])

    def test_6_mv_non_existent_items(self):
        with self.assertRaises(KeyError):
            self.pboard.move_item_by("T42", 10, True)

        sub_item = create_default_item(False)
        sub_item["id"] = "T42"
        sub_item["parent"] = "M42"
        self.pboard.insert(sub_item)
        with self.assertRaises(KeyError):
            self.pboard.move_item_by("T42", 10, True)

    def tearDown(self):
        self.pboard.__database__.close()


class TestHelperMethods(unittest.TestCase):
    def test_generate_id(self):
        time = datetime.now()
        result = generate_id(time)
        self.assertEqual(str(time).replace(" ", "-"), result)

        result_2 = generate_id()
        self.assertEqual(len(result), len(result_2))

    def test_generate_default_item(self):
        item = create_default_item()
        today = datetime.now().date().isoformat()

        self.assertEqual(item["name"], "default project")
        self.assertEqual(item["category"], "project")
        self.assertEqual(item["description"], "new default project")
        self.assertEqual(item["startdate"], today)
        self.assertEqual(item["duedate"], today)
        self.assertEqual(item["state"], "Open")
        self.assertEqual(item["parent"], None)
        self.assertEqual(item["sub_items"], [])

    def test_move_item_in_list(self):
        actual_list = [f"{i}" for i in range(10)]

        move_item_in_list_by_n("0", actual_list, 4)
        self.assertEqual("0", actual_list[4])
        self.assertEqual("1", actual_list[0])
        self.assertEqual("9", actual_list[-1])

        move_item_in_list_by_n("9", actual_list, 4)
        self.assertEqual("0", actual_list[4])
        self.assertEqual("1", actual_list[0])
        self.assertEqual("9", actual_list[-1])

        move_item_in_list_by_n("9", actual_list, -1)
        self.assertEqual("0", actual_list[4])
        self.assertEqual("1", actual_list[0])
        self.assertEqual("9", actual_list[-2])
        self.assertEqual("8", actual_list[-1])

        move_item_in_list_by_n("5", actual_list, -10)
        self.assertEqual("0", actual_list[5])
        self.assertEqual("5", actual_list[0])
        self.assertEqual("8", actual_list[-1])

    def test_read_metadata(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_file = "test1.json"
        filename = os.path.join(test_dir, test_file)

        metadata = read_metadata(filename)
        self.assertEqual(metadata["name"], "test1")
        self.assertEqual(metadata["filename"], "test1.json")
        self.assertEqual(metadata["description"], "")
