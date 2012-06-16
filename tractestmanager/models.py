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
from trac.wiki import WikiPage
from trac.core import TracError

import db_models
from db_models import NOT_TESTED, PASSED, FAILED, PASSED_COMMENT
from macros import TestPlanMacro

SUMMARY = 'summary'
OWNER   = 'owner'
STATUS  = 'status'

class TestCase(object):
    """ Testcase with attributes and and a list of actions.
    """

    def __init__(self, env, **kwargs):
        self.db= db_models.DbLite(env)
        self.actions = []

        for key in db_models.TC_KEYS: setattr(self, key, None)

        if kwargs:
            for key, value in kwargs.iteritems():
                setattr(self, key, value)

    def getattrs( self ):
        """ Returns a list of tuples.
        
        e.g.  [('wiki', 'DocTest'), ('description', 'bla'), ...]
        """
        return zip( db_models.TC_KEYS, 
                map( lambda x: getattr( self, x), db_models.TC_KEYS ))

    def insert(self):
        """Saves the testcase and its actions into the database.
        """

        # build a list of action dicts
        actionsattrs= list()
        for action in self.actions: actionsattrs.append( dict(action.getattrs()))

        self.db.insertTestCase( dict(self.getattrs()), actionsattrs )

class TestAction(object):
    """ Testaction with attributes as part of a testcase.
    """

    def __init__(self, env, **kwargs):
        for key in db_models.TA_KEYS: setattr(self, key, None)

        if kwargs:
            for key, value in kwargs.iteritems():
                setattr(self, key, value)

    def getattrs( self ):
        """ Returns a list of tuples.
        
        e.g.  [('title', 'Create WS'), ('description', 'bla'), ...]
        """
        return zip(db_models.TA_KEYS, 
                map( lambda x: getattr( self, x), db_models.TA_KEYS ))

    def set_status(self, status, comment=None):
        """
        >>> testaction = TestActionFilter(taid=1)[0]
        >>> testaction.set_status(status="OK", comment="Hello World")
        """
        pass
 
class TestRun(object):
    """ TestRun based on a trac ticket of type testrun it contains a list of
    testcases with their testactions.

    properties:
        env        -> the trac env
        runid      -> the testrun aka ticket id
        ticket     -> the trac ticket of type testrun
        wikiplan   -> the trac Wikipage with the testplan macro (which
                       contains the testcases)
        owner      -> the testrun aka ticket owner
        summary    -> the testrun aka ticket summary
        testcases  -> the list of validated TestCase instances of the testrun
    """

    @property
    def id(self): return self.runid

    @property
    def summary(self): return self.ticket[SUMMARY]
    @summary.setter
    def summary(self, value): self.ticket[SUMMARY] = value

    @property
    def owner(self): return self.ticket[OWNER]
    @owner.setter
    def owner(self, value): self.ticket[OWNER] = value

    @property
    def created(self): return self.ticket['time']

    exists = property(lambda self: self.runid is not None)

    @property
    def status(self): return self.ticket['status']

    def __getitem__(self, name):
        return getattr( self, name)

    def __setitem__(self, name, value):
        setattr(self, name, value)

    def __init__(self, env, runid= None):
        self.env= env
        self.dbg= env.log.debug
        self.dbg('TestRun( runid= %s )' % str(runid))

        self.testcases= list()

        # get the testrun based ticket ...
        if runid is not None: 
            self.runid= int(runid)
            self.ticket = Ticket(self.env, self.runid)

            self.wikiplan= WikiPage(self.env, self.ticket[SUMMARY])

        # ... or init a new (empty) one.
        else:
            self.ticket = Ticket(env)

    def setup(self, pagename, manager):
        """ Sets up a new testrun and inserts a new  trac ticket of type
        testrun into the database.
        """
        self.dbg('TestRun.setup( %s, %s )' % (str(pagename), str(manager)))

        self.wikiplan = WikiPage(self.env, pagename)

        # add new testrun ticket
        data = {
            OWNER          : manager,
            'reporter'     : manager,
            SUMMARY        : self.wikiplan.name,
            'description'  : self.wikiplan.text,
            'type'         : 'testrun',
        }
        self.dbg('tickte data: %s' % data)

        try:
            self.ticket.populate(data)
            self.runid = self.ticket.insert()
        except TracError, e:
            raise TracError( "TestRun ticket could not be created: %s" %
                    e.message )

        self.dbg('runid =  %d' % self.runid)
        return self.runid

    def validate(self):
        """validates the testrun: parse the testplan macro for testcase names and
        testers, and parse those testcases (wiki pages) to get and validate the
        actions and expected results.
        
        A test plan macrco looks like this:
        #! TestPlan 
        Id: TA14
        Testart: UsecaseTest 
        Build: DC-3.1.1
        Konfiguration: IE7-Win, FF-LUX
        Usecases: BaugruppenVerwalten, ObjekteSuchen

        Testcases/SaveAsEinerBaugruppe mmuster
        TcErzeugenEinerBaugruppe lmende, mmuster
        """
        self.dbg('TestRun.validate()')

        try:
            attributes, tc_tester_tups = TestPlanMacro(self.env).parse_config(
                    self.wikiplan.text)
        except TracError, e:
            raise TracError( "No testplan found on, parser error on %s, %s" %
                    (self.wikiplan.name, e.message))

        # TODO: verify that tc_tester_tups are valid

        # now parse (get) all testcases from tc_tester_tups
        from TestcaseParser import TestcaseParser
        parser = TestcaseParser(self.env)
        errors = dict()
        self.testcases= list()

        for pagename, tester in tc_tester_tups.iteritems():
            try:
                tc = parser.parseTestcase(pagename= pagename)
                tc.tester = tester
                tc.testrun = self.runid
                tc.status = NOT_TESTED

                for ta in tc.actions:
                    ta.testrun = self.runid
                    ta.status = NOT_TESTED
            except TracError, e:
                errors[pagename] = e.message
                continue
            self.testcases.append(tc)

        if errors:
            self._set_defect(self.env, errors)
            raise TracError( 
                "Testplan could not be started, for more information "\
                "review the testplan page '%s' and restart the testplan" % 
                self.wikiplan.name)

    def start(self):
        """
        inserts all testcases and their actions to the database and sets the
        testrun based ticket status to 'accepted'.
        """
        self.dbg('TestRun.start()')
        self.validate()
        for tc in self.testcases:
            tc.insert()
        self._set_accepted()
        return 

    def _set_defect(self, errors= None):
        self.dbg('TestRun._set_defect()')
        self.ticket[STATUS] = 'new'
        # TODO: for error in error_messages:
            #t['description'] += error
        return self.ticket.save_changes()

    def _set_accepted(self):
        self.dbg('TestRun._set_accepted()')
        self.ticket[STATUS] = 'accepted'
        return self.ticket.save_changes()

class TestCaseFilter(object):
    """
    filters testcases from db.
    """
    def __init__(self, env):
        self.env= env

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
            testaction = TestActionFilter(self.env).get()[0]
            testaction.id = i
            actions.append(testaction)
        return [TestCase(self.env, id="1", wiki="TcDocCreate", description="create a document in the workspace", title="= TcDocCreate =", revision="3", tester="lmende", testrun="2", status=NOT_TESTED, actions=actions)]

class TestActionFilter(object):
    """
    filters testactions from db.
    """
    def __init__(self, env):
        self.env= env

    def get(self, **kwargs):
        return [TestAction(self.env, id=1, testrun="1", tcid="1", 
            description="create a document in the workspace", 
            title="set doRunRun True", expected_result="run forever", 
            status=NOT_TESTED, comment=None)]


class TestRunQuery(object):
    """ query testruns through trac query
        testruns = TestRun().query(env, status=new)
        testrun returns a list of tickets with type=testrun and status=new
    """

    def __init__(self, env, **kwargs):
        self.env= env

        if kwargs:
            querystring = 'type=testrun'
            for key, value in kwargs.iteritems():
                querystring += '&%s=%s' % (key, value)
            self.query = TicketQuery.from_string(env, querystring)
        else:
            # query * testrun tickets
            self.query = TicketQuery.from_string(env, 'type=testrun')


    def execute(self):
        """Executes the trac ticket query and returns a list of TestRun instances.
        
            returns a list of tickets.
        """
        testruns = list()

        ticket_dicts = self.query.execute()
        for t in ticket_dicts:
            testruns.append(TestRun( self.env, t['id']))
        return testruns

# vim: set ft=python ts=4 sw=4 expandtab :
