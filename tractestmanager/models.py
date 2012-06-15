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
from trac.wiki import WikiPage
from trac.core import TracError
from macros import TestPlanMacro

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

        self.db.insertTestCase( self.getattrs(), actionsattrs )

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

    def set_status(self, status, comment=None):
        """
        >>> testaction = TestActionFilter(taid=1)[0]
        >>> testaction.set_status(status="OK", comment="Hello World")
        """
        pass

class TestRun(object):
    """ TestRun model
        This is a ticket
    """

    # TODO: refactor to deliver a list of testruns
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
            tc['status']  = ticket.values['status']
            testruns.append(tc)
        return testruns

    def setup(self, env, pagename, manager, runid=None):
        self.wikiplan = WikiPage(env, pagename)
        # now we reuse the macro to get the things done
        # we get two variables - testcases as a dict: {'Testcases/UC011':'johndoe'}
        try:
            attributes, testcases = TestPlanMacro(env).parse_config(self.wikiplan.text)
        except TracError:
            raise TracError("No testplan found on %s" % pagename)
        self.attributes = attributes
        self.testcases = testcases
        # add new testrun ticket
        if not runid:
            try:
                self._init_ticket(env, manager)
            except TracError:
                raise "TestRun could not be initiated"
        else:
            ticket = Ticket(env, runid)
            self.tid = ticket.id

        from TestcaseParser import TestcaseParser
        parser = TestcaseParser(env)
        # TODO: verify that testcases are valid
        self.errors = dict()
        for pagename, user in self.testcases.iteritems():
            try:
                testcase = parser.parseTestcase(pagename=pagename)
                testcase.tester = user
                testcase.testrun = self.tid
                testcase.status = NOT_TESTED
                # XXX: this is gaylord - we have to set a testrun,
                # status to a testaction - not needed (foreign key)
                for testaction in testcase.actions:
                    #testaction.kwargs['testrun'] = testrun.id
                    testaction.testrun = self.tid
                    testaction.status = NOT_TESTED
            except TracError, e:
                self.errors[pagename] = e.message
                continue
        if self.errors:
            self._set_defect(env, self.errors)
            raise TracError("Testplan could not be started, for more information review the testplan page '%s' and restart the testplan" % self.wikiplan.name)
        if runid:
            self._set_accepted(env)
        #else save :)

    def _init_ticket(self, env, user):
        data = dict()
        data['owner'] = user
        data['reporter'] = user
        data['summary'] = self.wikiplan.name
        data['description'] = self.wikiplan.text
        data['keywords'] = self.attributes['id']
        data['type'] = 'testrun'
        data['status'] = 'accepted'
        t = Ticket(env)
        t.populate(data)
        self.tid = t.insert()

    def _set_defect(self, env, error_messages):
        t = Ticket(env, self.tid)
        t['status'] = 'new'
        #for error in error_messages:
            #t['description'] += error
        return t.save_changes()

    def _set_accepted(self, env):
        t = Ticket(env, self.tid)
        t['status'] = 'accepted'
        return t.save_changes()

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
        actions = list()
        i = 5
        while i>0:
            i = i-1
            testaction = TestActionFilter().get()[0]
            testaction.id = i
            actions.append(testaction)
        return [TestCase(id="1", wiki="TcDocCreate", description="create a document in the workspace", title="= TcDocCreate =", revision="3", tester="lmende", testrun="2", status=NOT_TESTED, actions=actions)]

class TestActionFilter(object):
    """
    filters testactions from db.
    """
    def get(self, **kwargs):
        return [TestAction(id=1, testrun="1", tcid="1", description="create a document in the workspace", title="set doRunRun True", expected_result="run forever", status=NOT_TESTED, comment=None)]

# vim: set ft=python ts=4 sw=4 expandtab :
