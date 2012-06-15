# -*- coding: utf-8 -*-
#
# File: interfaces.py
#
# Copyright (c) InQuant GmbH
#

__author__ = 'Rainer Hihn <rainer.hihn@inquant.de>'
__docformat__ = 'plaintext'

from trac.core import *
from trac.env import IEnvironmentSetupParticipant
from trac.db import Table, Column, Index


class TestManagerModelProvider(Component):
    implements(IEnvironmentSetupParticipant)

    SCHEMA = [
          Table('testaction', key = ('id'))[
            Column('id', type= 'int', auto_increment= True),
            Column('tcid', type= 'int'),
            Column('testrun', type= 'int'),
            Column('title'),
            Column('description'),
            Column('expected_result'),
            Column('status'),
            Column('comment'),
            Index(['id', 'title'])],

          Table('testcase', key = ('tcid'))[
            Column('tcid', type= 'int', auto_increment= True),
            Column('wiki'),
            Column('title'),
            Column('description'),
            Column('revision'),
            Column('tester'),
            Column('testrun', type= 'int' ),
            Column('status'),
            Index(['tcid', 'wiki', 'title', 'testrun'])],
        ]

    # IEnvironmentSetupParticipant methods
    def environment_created(self):
        self._upgrade_db(self.env.get_db_cnx())
        
    def environment_needs_upgrade(self, db):
        if self._need_migration(db):
            return True
        return False

    def upgrade_environment(self, db):
        self._upgrade_db(db)

    def _need_migration(self, db):
        try:
            cursor = db.cursor()
            cursor.execute("select * from testaction")
            return False
        except Exception, e:
            self.log.error("DatabaseError: %s", e)
            db.rollback()
            return True

    def _upgrade_db(self, db):
        try:
            try:
                from trac.db import DatabaseManager
                db_backend, _ = DatabaseManager(self.env)._get_connector()
            except ImportError:
                db_backend = self.env.get_db_cnx()

            cursor = db.cursor()
            for table in self.SCHEMA:
                for stmt in db_backend.to_sql(table):
                    self.env.log.debug(stmt)
                    cursor.execute(stmt)
            db.commit()
        except Exception, e:
            self.log.error("DatabaseError: %s", e)
            db.rollback()
            raise
