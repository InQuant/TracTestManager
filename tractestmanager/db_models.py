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

from trac.core import Component
import trac.db
from trac.db import with_transaction

__author__ = 'Otto Hockel <otto.hockel@inquant.de>'
__docformat__ = 'plaintext'

#def initenv(_env):
    #global ENV
    #ENV = _env

class DbException(Exception):
    pass
class DbAlreadyExistException(DbException):
    pass

class DbTestCases(Component):
    """ Wrap the database to query TestCases
    """

    def get(self):
        @with_transaction(self.env)
        def _get(self, db, **kwargs):
            cursor = db.cursor()
            stmt = ("SELECT wiki,title,revision,tester,testrun,status"
                           "FROM testcases "
                           "WHERE")
            for key, value in dict(KeyValues):
                stmt = ("%s AND %s=%s" % (stmt, key, value))
            cursor.execute(stmt)
            row = cursor.fetchone()
            pass

    def tcCreate(self, **kwargs):
        @with_transaction(self.env)
        def _tcCreate(db, kwargs):
            cursor = db.cursor()
            cursor.execute("""INSERT INTO testcases 
                (wiki,title,revision,tester,testrun,status)
                VALUES (%(wiki)s,%(title)s,%(revision)s,%(tester)s,%(testrun)s,%(status)s)""" % kwargs)

class TracDBModel(object):
    """ Generic DB Model
    """

    def __init__(self, env):
        self.env = env
        #self.db  = env.get_db_cnx()
        #self.cursor = self.db.cursor()

    def __repr__(self):
        return "<TestManager:TracDBModel>"

class Testcase(TracDBModel):
    """ Testcase model
    """

    id       = None
    wiki     = None
    title    = None
    # the wiki page revision to take
    revision = None
    tester   = None
    # one testcase has one or more actions
    actions  = list()
    # one or more testcases belong to one testrun
    testrun  = None
    status   = None

    # a Testcase can be initialized with an existing id.
    # if the id exists, the full object will be loaded

    def __init__(self, env, id=None):
        if id is not None:
            super(Testaction, self).__init__(env)
            # TODO: exception handling if testaction not in db
            self.id = id
            self._fetch(id, self.db)
        else:
            # TODO: not implemented yet, for insertion purpose
            pass

    def __repr__(self):
        return '<Testcase: "%s">' % (self.title)

    def _fetch(self, id, db=None):
        if not db:
            db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("SELECT wiki,title,revision,tester,testrun,status"
                       "FROM testcases "
                       "WHERE id=%s", int(id))
        row = cursor.fetchone()
        # if not row -> testcase not available
        if row:
            wiki, title, revision, tester, testrun, status = row
            self.wiki     = wiki
            self.title    = title
            self.revision = revision
            self.tester   = tester
            self.testrun  = testrun
            self.status   = status
            self.id       = id
            # Fetch all testactions for this testcase
            # "SELECT * FROM testactions WHERE testcase_id=%s", int(id)
            # for row in cursor.fetchall(): testactions.append(row)
            #pass

    def get_actions(self, db=None):
        actions = list()
        @self.env.with_transaction(db)
        def do_load_actions(db):
            cursor = db.cursor()
            cursor.execute("SELECT id,description,expected_result"
                           "FROM testactions "
                           "WHERE testcase=", int(self.id))
            rows = cursor.fetchall()
            for row in rows:
                actions.append(row)
        # return Testactions
        return actions

    def save(self, db=None):
        @self.env.with_transaction(db)
        def do_save(db):
            cursor = db.cursor()
            cursor.execute("""
                    INSERT INTO testcases (wiki,title,revision,tester,
                                           actions,testrun,status)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    """, (self.wiki, self.title, self.revision, self.tester,
                        self.testrun, self.status))

    def delete(self, db=None):
        @self.env.with_transaction(db)
        def do_save(db):
            pass
        pass

    def check_integrity(self):
        # TODO: check integrity of the whole testaction
        #       return errors and things like this
        return True

class Testaction(TracDBModel):
    """ Testaction model
        an action is part of a testcase
    """

    id              = None
    # one or more testactions belong to one testcase
    testcase        = None
    # the comment is appended to the testrun. for the
    # purpose of integrity, we need the action as base
    comment         = None
    status          = None
    description     = None
    expected_result = None

    # a Testaction can be initialized with an existing id.
    # if the id exists, the full object will be loaded

    def __init__(self,env,id=None):
        if id is not None:
            super(Testaction, self).__init__(env)
            # TODO: exception handling if testaction not in db
            self.id = id
            self._fetch(id, self.db)
        else:
            # TODO: not implemented yet, for insertion purpose
            pass

    def _fetch(self, id, db=None):
        if not db:
            db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("SELECT testcase,comment,status,description,expected_result"
                       "FROM testactions "
                       "WHERE id=%s", int(id))
        row = cursor.fetchone()
        # if not row -> testcase not available
        if row:
            testcase, comment, status, description, expected_result = row
            self.testcase = testcase
            self.comment = comment
            self.status = status
            self.description = description
            self.expected_result = expected_result
            self.id = id

    def __repr__(self):
        return '<Testaction: "%s">' % (self.title)

    def save(self, db=None):
        pass

    def delete(self, db=None):
        pass

    def getXML(self, id, db=None):
        pass

    def check_integrity(self):
        # TODO: check integrity of the whole testaction
        #       return errors and things like this
        return True

class DbTestcases(object):
    
    def get(self, kwargs):
        pass

# vim: set ft=python ts=4 sw=4 expandtab :
