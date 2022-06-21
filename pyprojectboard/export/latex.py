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
from os.path import splitext
import subprocess

# pylint: disable=import-error
from pylatex import Command
from pylatex import Document
from pylatex import HFill
from pylatex import Itemize
from pylatex import NewLine
from pylatex import Section
from pylatex import Subsection
from pylatex import Subsubsection
from pylatex.base_classes import Environment
from pylatex.package import Package
from pylatex.table import Tabular
from pylatex.utils import bold
from pylatex.utils import NoEscape
# pylint: enable=import-error


def export(projectboard, generate_pdf=False):

    filename = splitext(projectboard.get_metadata('filename'))[0]
    doc = Document(filename)

    doc.packages.append(Package('progressbar'))

    doc.preamble.append(Command('title', projectboard.get_metadata('name')))
    author = projectboard.get_metadata('author')
    if author:
        doc.preamble.append(Command('author', 'Created by ' + author))
    doc.preamble.append(Command('date', NoEscape(r'\today')))
    cmd_abstract_title = r'\renewcommand{\abstractname}{Description}'
    doc.preamble.append(NoEscape(cmd_abstract_title))
    doc.append(NoEscape(r'\maketitle'))

    class Abstract(Environment):
        pass

    desc = Abstract()
    desc.append(Command('centering'))
    desc.append(Command('large'))
    desc.append(projectboard.get_metadata('description'))
    doc.append(desc)

    doc.append(NoEscape(r'\tableofcontents'))

    project_summary(doc, projectboard)
    projects(doc, projectboard)

    doc.generate_tex()
    if generate_pdf:
        try:
            doc.generate_pdf(clean_tex=False)
        except subprocess.CalledProcessError:
            print("error")
    print("export finished")


def project_summary(doc, projectboard):

    doc.append(Section('Summary'))
    pb_config = ['filledcolor=red',
                 'emptycolor=green',
                 'width=5cm',
                 'subdivisions=5']

    cmd_pb_config = Command('progressbarchange', ', '.join(pb_config))
    doc.append(cmd_pb_config)
    tab = Tabular('c|c|c')
    tab.add_hline()
    tab.add_hline()
    tab.add_row(('Name', 'Progress', 'Duedate'))
    tab.add_hline()
    pids = projectboard.get_ids()
    for pid in pids:
        project = {}
        projectboard.project(pid, project)
        cmd_prog = Command('progressbar', project['progress'] / 100)
        tab.add_row((project['name'], cmd_prog, project['duedate']))
        tab.add_hline()

    tab.add_hline()
    doc.append(tab)


def projects(doc, projectboard):

    doc.append(Section('Projects'))
    pids = projectboard.get_ids()
    for pid in pids:
        project = {}
        projectboard.project(pid, project)
        doc.append(Subsection('Project: ' + project['name']))
        doc.append(bold('Duedate: ' + project['duedate']))
        doc.append(HFill())
        doc.append(bold('State: ' + project['state']))
        doc.append(NewLine())
        doc.append(bold('Description: '))
        doc.append(project['description'])
        tids = project['task_ids']
        add_tasks(doc, projectboard, tids)


def add_tasks(doc, projectboard, tids):

    doc.append(Subsubsection('Tasks'))
    itemize = Itemize()
    for tid in tids:
        task = {}
        projectboard.task(tid, None, task)
        item = [task['name'], '\\hfill',
                bold('Duedate: '), task['duedate'],
                '\\\\',
                bold('State: '), task['state'],
                '\\\\',
                bold('Description: '), task['description']]
        itemize.add_item(NoEscape(''.join(item)))
    doc.append(itemize)
