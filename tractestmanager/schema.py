# -*- coding: utf-8 -*-
#
# File: interfaces.py
#
# Copyright (c) InQuant GmbH
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

__author__ = 'Rainer Hihn <rainer.hihn@inquant.de>'
__docformat__ = 'plaintext'

from trac.core import *
from trac.env import IEnvironmentSetupParticipant
from trac.db import Table, Column, Index


class TestManagerModelProvider(Component):
    implements(IEnvironmentSetupParticipant)

    SCHEMA = [
          Table('testaction', key = ('id'))[
            Column('id'),
            Column('testcase'),
            Column('status'),
            Column('description'),
            Column('expected_result'),
            Index(['id'])],
          Table('testcase', key = ('id'))[
            Column('id'),
            Column('wiki'),
            Column('title'),
            Column('revision'),
            Column('tester'),
            Column('testrun'),
            Column('status'),
            Column('actions'),
            Index(['id'])]
        ]

    # IEnvironmentSetupParticipant methods
    def environment_created(self):
        self._upgrade_db(self.env.get_db_cnx())
        
    def environment_needs_upgrade(self, db):
        if self._need_migration(db):
            return True

    def upgrade_environment(self, db):
        self._upgrade_db(db)

    def _need_migration(self, db):
        pass

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
