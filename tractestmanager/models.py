# -*- coding: utf-8 -*-
#
# File: TestPlan.py
#
# Copyright (c) Inquant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from db_models import *

NOT_TESTED= 'not tested'

class TestCase(object):
    """ Testcase model
    """

    wiki     = None
    title    = None
    revision = None
    tester   = None
    testrun  = None # ticket number
    status   = None
    actions  = list()

    def __init__(self, wiki = None, title = None, revision = None, tester = None, testrun = None, status = None):
        self.wiki     = wiki
        self.title    = title
        self.revision = revision
        self.tester   = tester
        self.testrun  = testrun
        self.status   = status

    def save(self):
        # TODO: should save testcase and actions into database
        pass

class TestAction(object):
    """ Testaction model
        an action is part of a testcase
    """

    testcase        = None
    comment         = None
    status          = None
    description     = None
    expected_result = None

    def save(self):
        # TODO: should save actions into database
        pass

class TestRun(object):
    """ TestRun model
    """

    ticket = None


class TestCaseFilter(object):
    """
    filters testcases from db.
    """
    
    def get(self, **kwargs):
        dbtcs     = DbTestcases()
        tcrows    = dbtcs.query(kwargs)
        testcases = list()

        for row in tcrows:
            testcases.append(Testcase(row))

        # return testcases
        return [TestCase("TcDocCreate", title = "= TcDocCreate =", revision = "3", tester = "lmende", testrun = "2", status = NOT_TESTED)]

# vim: set ft=python ts=4 sw=4 expandtab :
