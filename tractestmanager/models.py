# -*- coding: utf-8 -*-
#
# File: models.py
#
# Copyright (c) Inquant GmbH
#

__author__ = 'Otto Hockel <otto.hockel@inquant.de>'
__docformat__ = 'plaintext'

from trac.ticket.query import Query as TicketQuery
from trac.ticket.model import Ticket
import db_models
from db_models import NOT_TESTED, PASSED, FAILED, PASSED_COMMENT

class TestCase(object):
    """ Testcase model
    """

    def __init__(self, **kwargs):
        db= db_models.DbLite()
        self.actions = []
        self.errors = {}
        for key in db_models.TC_KEYS: setattr(self, key, None)

        if kwargs:
            for key, value in kwargs.iteritems():
                setattr(self, key, value)

    def getattrs( self ):
        return map( lambda x: getattr( self, x), db_models.TC_KEYS )

    def insert(self):
        # TODO: should save testcase and actions into database

        # build a list of action dicts
        actionsattrs= list()
        for action in self.actions: actionsattrs.append( action.getattrs() )

        db.insertTestCase( self.getattrs(), actionsattrs )

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
        self.broken = False

        for key in db_models.TA_KEYS: setattr(self, key, None)

        if kwargs:
            for key, value in kwargs.iteritems():
                setattr(self, key, value)

    def getattrs( self ):
        return map( lambda x: getattr( self, x), db_models.TA_KEYS )

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
