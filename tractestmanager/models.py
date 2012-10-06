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

import string
import re

import db_models
from testmanconst import *

from TestManagerLib import safe_unicode

SUMMARY = 'summary'
OWNER   = 'owner'
STATUS  = 'status'
STATUSES = [PASSED, PASSED_COMMENT, SKIPPED, FAILED, NOT_TESTED]

def test_status():
    return [SKIPPED, NOT_TESTED, PASSED, FAILED, PASSED_COMMENT]

class TestItem(object):
    """ Core class for test cases and test actions.
    """
    def __init__(self, env, dbtable, keys, attributes={}):
        env.log.debug('TestItem( %s )' % attributes)
        self.dbg= env.log.debug

        self.env= env
        self.db= db_models.DbLite(env)
        self.dbtable= dbtable

        self._update= {}
        self.keys= keys

        for key in keys: setattr(self, key, None)

        if attributes:
            for key, value in attributes.iteritems():
                setattr(self, key, value)

    def __getitem__(self, name):
        return getattr( self, name)

    def getattrs( self ):
        """ Returns a list of tuples.

        e.g.  [('wiki', 'DocTest'), ('description', 'bla'), ...]
        """
        return zip( self.keys,
                map( lambda x: getattr( self, x, None), self.keys ))

    def _prepare_for_update(self, **kwargs):
        """ pushs the attributes to be updated on the _update stack.
        """
        if kwargs: self._update.update(kwargs)

    def save_changes(self):
        """ saves the changed attributes which exist on the _updated stack to db.
        """
        self.dbg('%s.save_changes()')
        self.dbg(self._update)
        stmt= string.join( [k + '=%s' for k in self._update.keys()], ', ')
        self.dbg(stmt)
        self.db.updateTestItem( self.dbtable, self.id, stmt, self._update.values() )


class TestCase(TestItem):
    """ Testcase with attributes and and a list of actions.
    """

    def __init__(self, env, attributes={}):
        env.log.debug('TestCase( %s )' % attributes)
        TestItem.__init__(self, env, TC_TABLE, TC_KEYS, attributes)

        self._actions = list()

    @property
    def actions(self):
        id= getattr(self, 'tcid', None)
        if self._actions:
            return self._actions
        elif id is not None:
            self._actions= TestActionQuery(self.env, tcid= self.tcid).execute()
            return self._actions
        else:
            return []

    @property
    def id(self): return getattr( self, 'tcid', None )

    def add_action(self, action):
        self._actions.append(action)

    def insert(self):
        """Saves the testcase and its actions into the database.
        """

        # build a list of action dicts
        actionsattrs= list()
        for action in self.actions: actionsattrs.append( dict(action.getattrs()))

        return self.db.insertTestCase( dict(self.getattrs()), actionsattrs )

    def set_status(self):
        """ sets the status of an test case, the worst status wins.
        """
        self.dbg('TestCase.set_status()')

        overall_status = PASSED
        old_status = TestCaseQuery(self.env, tcid=self.id).execute()[0].status
        for action in self.actions:
            if STATUSES.index(action.status) > STATUSES.index(overall_status):
                overall_status = action.status

        if STATUSES.index(overall_status) != old_status:
            setattr(self, '_status', overall_status)
            self._prepare_for_update( status= overall_status )
            self.save_changes()

class TestItemGroupStats(object):
    """ Encapsulates statistics on a group of test items (actions or cases).

    adapted from trac TicketGroupStats
     [
         interval{
         'count': 1
         'title': PASSED
         'css_class': 'closed'
         'percent': 7.0
         'overall_completion': True
         'qry_args': {'status': [PASSED]}
         }

         interval{
         'count': 11
         'title': SKIPPED
         'css_class': 'open'
         'percent': 93.0
         'overall_completion': False
         'qry_args': {'status': [SKIPPED, NOT_TESTED]}
         }
     ]
    """

    def __init__(self, title, unit):
        """
        :param title: the display name of this group of stats (e.g.
                      ``'test action status'``)
        :param unit: is the units for these stats in plural form,
                     e.g. ``_('hours'``)
        """
        self.title = title
        self.unit = unit
        self.count = 0
        self.qry_args = {}
        self.intervals = []
        self.done_percent = 0
        self.done_count = 0

    def add_interval(self, title, count, qry_args, css_class,
                     overall_completion=None):
        """Adds a division to this stats' group's progress bar.

        :param title: the display name (e.g. ``'closed'``, ``'spent
                      effort'``) of this interval that will be
                      displayed in front of the unit name
        :param count: the number of units in the interval
        :param qry_args: a dict of extra params that will yield the
                         subset of tickets in this interval on a query.
        :param css_class: is the css class that will be used to
                          display the division
        :param overall_completion: can be set to true to make this
                                   interval count towards overall
                                   completion of this group of
                                   tickets.
        """
        self.intervals.append({
            'title': title,
            'count': count,
            'qry_args': qry_args,
            'css_class': css_class,
            'percent': None,
            'overall_completion': overall_completion,
        })
        self.count = self.count + count

    def refresh_calcs(self):
        if self.count < 1:
            return
        total_percent = 0
        self.done_percent = 0
        self.done_count = 0
        for interval in self.intervals:
            interval['percent'] = round(float(interval['count'] /
                                        float(self.count) * 100))
            total_percent = total_percent + interval['percent']
            if interval['overall_completion']:
                self.done_percent += interval['percent']
                self.done_count += interval['count']

        # We want the percentages to add up to 100%. To do that, we fudge one
        # of the intervals. If we're <100%, we add to the smallest non-zero
        # interval. If we're >100%, we subtract from the largest interval.
        # The interval is adjusted by enough to make the intervals sum to 100%.
        if self.done_count and total_percent != 100:
            fudge_amt = 100 - total_percent
            fudge_int = [i for i in sorted(self.intervals,
                                           key=lambda k: k['percent'],
                                           reverse=(fudge_amt < 0))
                         if i['percent']][0]
            fudge_int['percent'] += fudge_amt
            self.done_percent += fudge_amt

class TestAction(TestItem):
    """ Testaction with attributes as part of a testcase.
    """

    def __init__(self, env, attributes={}):
        env.log.debug('TestAction( %s )' % attributes)
        TestItem.__init__(self, env, TA_TABLE, TA_KEYS, attributes)
        self.env= env
        self._comments = list()

    @property
    def comments(self):
        testrun= getattr(self, 'testrun', None)
        if self._comments:
            return self._comments
        elif testrun is not None:
            self._populate_action_comments()
            return self._comments
        else:
            return []


    def set_status(self, status, comment=None):
        """ sets the status and comment of an test action.
        """
        self.dbg('TestAction.set_status( %s, %s)' % (str(status), str(comment)))

        if status not in STATUSES:
            raise TracError("Wrong status for a test action")

        if status == FAILED and comment == None:
            raise TracError("This status must be commented.")

        setattr(self, 'status', status)
        self._prepare_for_update( status= status )

        if comment:
            setattr(self, 'comment', comment)
            self._prepare_for_update( comment= comment )

        self.save_changes()

        # check if testcase is fully tested
        TestCase(self.env, {'tcid': self.tcid}).set_status()

    def _populate_action_comments(self):
        t = Ticket(self.env, self.testrun)
        history = t.get_changelog()
        pat = re.compile(r"(\b(ta_id)=([0-9]+))")
        for change in history:
            # we get a list of change attributes [...,...,"user","comment",...]
            # (datetime.datetime(2012, 6, 25, 7, 19, 7, 742580, tzinfo=<FixedOffset "UTC" 0:00:00>),
            #  u'testadmin',
            #  u'comment',
            #  u'2', 
            #  u'\npassed with comment "Check menu and toolbar" in 
            #  [http://localhorst:8000/trac/TestManager/general/testcase/23 TestCase #23]
            #  for [wiki:Testcases/UC012?revision=None]\n\ntoo slow\n', 1)
            match = pat.search(change[4])
            # if the ta_id is found, we have an association
            if match and int(match.group(3)) == self.id:
                self._comments.append({"user" : change[1], "text" : change[4]})


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

    @property
    def description(self):
        """ build the ticket desctiption
        """
        description_template = """
        = [wiki:%(wikiplan)s] =
        [[TestEval(testrun=%(testrun)s)]]
        [[TestRunMonitor(testrun=%(testrun)s)]]
        """
        data = {
                "testrun" : self.runid,
                "wikiplan" : self.wikiplan.name
                }
        description =  description_template % data
        return description

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
            'type'         : 'testrun',
        }
        self.dbg('ticket data: %s' % data)

        try:
            self.ticket.populate(data)
            self.runid = self.ticket.insert()
            self.ticket['description'] = self.description
            self.ticket.save_changes()
        except TracError, e:
            self.env.log.error(e)
            raise TracError( safe_unicode("TestRun ticket could not be created: %s" %
                    e.message ))

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
            from TestcaseParser import TestPlanMacroParser
            attributes, tc_tester_tups = TestPlanMacroParser(self.env).parse_config(
                    self._testplan_macro_content(self.wikiplan.text))
        except TracError, e:
            self.env.log.error(e)
            raise TracError( safe_unicode("Testplan error on %s, %s" %
                    (self.wikiplan.name, e.message)))

        # TODO: verify that tc_tester_tups are valid
        # FIX: tc_tester_tups were a dict instead of a tuple list

        # now parse (get) all testcases from tc_tester_tups
        from TestcaseParser import TestcaseParser
        parser = TestcaseParser(self.env)
        errors = dict()
        self.testcases= list()

        for pagename, testers in tc_tester_tups:
            for tester in testers:
                try:
                    tc = parser.parseTestcase(pagename= pagename)
                    tc.testrun = self.runid
                    tc.status = NOT_TESTED
                    tc.tester= tester

                    for ta in tc.actions:
                        ta.testrun = self.runid
                        ta.status = NOT_TESTED
                except TracError, e:
                    self.env.log.error(e)
                    errors[pagename] = safe_unicode(e.message)
                    continue

                self.testcases.append(tc)

        if errors:
            self._set_defect(errors)
            raise TracError(
                "Testplan could not be started, for more information "\
                "review the testplan page '%s' and restart the testplan" %
                self.wikiplan.name)

    def _testplan_macro_content( self, wikitext ):
        """ searches the testplan macro text in a wiki page.
        """
        self.dbg( "TestRun._testplan_macro_content()" )

        # pattern to search all text inside macro brackets
        pat= re.compile('\{\{\{[\r\n\s]*#\!\s*TestPlan(.*?)\}\}\}', re.MULTILINE and
                re.DOTALL)

        m= pat.search(wikitext)

        if m:
            return m.group(1)
        else:
            self.env.log.error('no testplan found')
            raise TracError('no testplan found')


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

class TestItemQuery(object):
    """ core query class.
    """

    def __init__(self, env, **kwargs):
        self.env= env
        self.db= db_models.DbLite(env)
        self.query= None
        self.values= []

        filter_keys= list()
        filter_vals= list()
        if kwargs:
            # build filter
            # e.g. 'testrun=%s AND (status=%s OR status=%s)
            # e.g. 'testrun=19 AND (status=not tested OR status=skipped)
            for key, val in kwargs.iteritems():
                # TODO: check if any value is a list
                if type(val) == list:
                    # construct OR clause
                    newkey= "(" + string.join(
                        ['%s=%%s' % key for i in range(len(val))], ' OR ') + ")"
                    filter_keys.append(newkey)
                    filter_vals.extend(val)
                else:
                    filter_keys.append("%s=%%s" % key)
                    filter_vals.append(val)

            self.query= string.join(filter_keys, ' AND ')
            self.values= filter_vals

class TestCaseQuery(TestItemQuery):
    """ query testcases from db.
    """

    def __init__(self, env, **kwargs):
        TestItemQuery.__init__(self, env, **kwargs)

    def execute(self):
        """Executes the db test case query and returns a list of TestCase instances.

        """
        testcases = list()

        rows= self.db.getTestCases( self.query, self. values )

        for row in rows:
            testcases.append(
                TestCase(self.env, dict(zip(db_models.TC_KEYS, row))))
        return testcases

class TestActionQuery(TestItemQuery):
    """ query testactions from db.
    """

    def __init__(self, env, **kwargs):
        TestItemQuery.__init__(self, env, **kwargs)

    def execute(self):
        """Executes the db test action query and returns a list of TestAction instances.
        """
        testactions = list()
        rows= self.db.getTestActions( self.query, self. values )

        for row in rows:
            testactions.append(
                TestAction(self.env, dict(zip(db_models.TA_KEYS, row))))
        return testactions

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
