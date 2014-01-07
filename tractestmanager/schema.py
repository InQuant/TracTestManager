# -*- coding: utf-8 -*-
#
# File: schema.py
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
            Column('tester'),
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
            # check if table should be created
            cursor.execute("select * from testaction")
            # we changed testaction table to save the tester in version 0.3.1
            # XXX: this is a hack to check this and alter
            self.upgrade_alter_table(db, "testaction", "tester", "char(30)")
            return False
        except Exception, e:
            self.log.error("DatabaseError: %s", e)
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
        except Exception, e:
            self.log.error("DatabaseError: %s", e)
            raise

    def upgrade_alter_table(self, db, tablename, colname, coltype):
        """ Does the alter table query if colname in tablename does not exist
        """
        try:
            cursor = db.cursor()
            cursor.execute("select %s from %s" % (colname,tablename))
        except Exception, e:
            self.log.debug("upgrade_alter_table: %s", e)
            cursor = db.cursor()
            alter = "ALTER TABLE %s add column %s %s" % (tablename, colname,
                    coltype)
            cursor.execute(alter)
