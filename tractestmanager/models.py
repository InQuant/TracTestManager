# -*- coding: utf-8 -*-
#
# File: models.py
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

__author__ = 'Otto Hockel <otto.hockel@inquant.de>'
__docformat__ = 'plaintext'

from trac.ticket.query import Query as TicketQuery
from trac.ticket.model import Ticket
import db_models

NOT_TESTED= 'not tested'

class TestCase(object):
    """ Testcase model
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.actions = []
        self.errors = {}
        if self.kwargs:
            for key, value in kwargs.iteritems():
                setattr(self, key, value)

    def save(self):
        # TODO: should save testcase and actions into database
        
        try:
            db_models.tcCreate(self.kwargs)
        except db_models.DbAlreadyExistException:
            db_models.tcUpdate(self.kwargs)

        for action in self.actions:
            try:
                db_models.actionCreate(action)
            except db_models.DbAlreadyExistException:
                db_models.actionUpdate(action)


class TestAction(object):
    """ Testaction model
        an action is part of a testcase
    """

    #testcase        = None
    #comment         = None
    #status          = None
    #description     = None
    #expected_result = None
    broken           = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.broken = False
        pass

    def save(self):
        # TODO: should save actions into database
        pass

class TestRun(object):
    """ TestRun model
    """

    #ticket = None
    def query(self, env, **kwargs):
        """ query testruns through trac query
            testruns = TestRun().query(env, status=new)
            testrun returns a list of tickets with type=testrun and status=new
            returns a list of tickets
        """
        tickets = list()
        testruns = list()
        if kwargs:
            querystring = 'type=testrun'
            for key, value in kwargs.iteritems():
                querystring += '&%s=%s' % (key, value)
            self.query = TicketQuery.from_string(env, querystring)
        else:
            # query * testrun tickets
            self.query = TicketQuery.from_string(env, 'type=testrun')
        ticket_dicts = self.query.execute()
        for t in ticket_dicts:
            tickets.append(Ticket(env, tkt_id=t['id']))

        for ticket in tickets:
            tc = {}
            tc['id']      = ticket.id
            tc['summary'] = ticket.values['summary']
            tc['created'] = ticket.time_created.ctime()
            testruns.append(tc)
        return testruns

class TestCaseFilter(object):
    """
    filters testcases from db.
    """
    
    def get(self, **kwargs):
        #dbtcs     = db_models.DbTestCases()
        #tcrows    = dbtcs.get(kwargs)
        #testcases = list()

        #for row in tcrows:
            #testcases.append(TestCase(row))

        # return testcases
        return [TestCase(id="1", wiki="TcDocCreate", description="create a document in the workspace", title="= TcDocCreate =", revision="3", tester="lmende", testrun="2", status=NOT_TESTED)]

# vim: set ft=python ts=4 sw=4 expandtab :
