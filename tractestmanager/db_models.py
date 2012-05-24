# -*- coding: utf-8 -*-
#
# File: db_models.py - wraps the trac sql stuff needed in testman
#
# Copyright (c) Inquant GmbH
#

__author__ = 'Lutz Mende <lutz.mende@inquant.de>'
__docformat__ = 'plaintext'

from trac.env import Environment
from trac.db import with_transaction
import trac.db

import logging
import string

LOGGER="db_models"
def debug(msg): logging.getLogger(LOGGER).debug(msg)

TRACENV= None

# modul exceptions
class DbException(Exception):
    pass
class DbAlreadyExistException(DbException):
    pass

# (case | action) status
NOT_TESTED= 'not tested'
PASSED= 'passed'
PASSED_COMMENT= 'passed with comment'
FAILED= 'failed'

# TestCase collumns
TC_KEYS= [ 'tcid', 'wiki', 'title', 'description', 'version', 'tester', 'testrun', 'status']
# TestAction collumns
TA_KEYS= ['testrun', 'tcid', 'title', 'description', 'expected_result', 'status', 'comment']

##############################################################################
def orderedValues(keys, adict):
    """
    Constructs the value list for insert operations in the right order.
    
    >>> keys= ['a', 'b', 'c']
    >>> adict= {'c':3, 'a':1, 'b':2}
    >>> orderedValues(keys, adict)
    [1, 2, 3]

    """
    return [adict.get(k, None) for k in keys]

##############################################################################
def getInsertPlaceHolders(keys):
    """
    Builds the tracdb required '%s' place holder list, 
    e.g.: the '%s, %s, %s, %s' string for 4 keys

    >>> keys= ['a', 'b', 'c']
    >>> getInsertPlaceHolders(keys)
    '%s, %s, %s'

    """
    return string.join(['%s' for i in range(len(keys))], ', ')

##############################################################################
class DbLite(object):
    """
    Class to wrap the SQL stuff about TestCases and TestActions ...

    >>> from trac.env import Environment
    >>> env= Environment( '/Users/lmende/Dropbox/projekte/BoschRexroth/TracTestManager/testman' )
    
    1. Instanciate the class and set it up aka create the tables.

    >>> db= DbLite(env)

    >>> db.setup()

    2. Build a dict for a Testcase to add.

    >>> tcvals= ['TcDocCreate', 'Create Docs', None, 2, 'lmende', 3, NOT_TESTED]

    3. Build a list of dicts for TestActions to add.

    >>> vals1= [ 3, None, 'Add to Workspace', 'Add to WS desc', 'Docs added',PASSED, None ]
    >>> vals2= [ 3, None, 'Checkout', 'Checkout desc', 'Docs checked out', NOT_TESTED, None ]
    >>> actions= [dict(zip(TA_KEYS, vals1)), dict(zip(TA_KEYS, vals2))]
    
    4. Insert the test case and actions.

    >>> db.insertTestCase( dict(zip(TC_KEYS[1:], tcvals)), actions )

    Get all testcases
    >>> db.getTestCases()
    [...]

    Get filtered testcases
    >>> db.getTestCases(status= NOT_TESTED)
    [...]

    Get all actions
    >>> db.getTestActions()
    [...]

    Get filtered actions
    >>> db.getTestActions(testrun= 3, status= NOT_TESTED)
    [...]

    """

    ##########################################################################
    def __init__(self):
        debug('DbLite.__init__()')
        self.env= TRACENV

    ##########################################################################
    def setup(self):
        """
        Sets up the two additional testman tables
        """
        debug('DbLite.setup()')

        @with_transaction(self.env)
        def _createTables(db):
            c= db.cursor()

            # create testcases table
            cols= string.join([
               'tcid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT',
               'wiki VARCHAR(512) NOT NULL',
               'title VARCHAR(512) NOT NULL',
               'description TEXT',
               'version INTEGER NOT NULL',
               'tester VARCHAR(80)',
               'testrun INTEGER NOT NULL',
               'status VARCHAR(80) NOT NULL',
                    ], ', ')

            stmt= """CREATE TABLE IF NOT EXISTS testcases (%s)""" % cols
            debug(stmt)
            c.execute(stmt)

            # create testactions table
            cols= string.join([
               'testrun INTEGER NOT NULL',
               'tcid INTEGER NOT NULL REFERENCES testcases (tcid)',
               'title VARCHAR(512) NOT NULL',
               'description TEXT',
               'expected_result TEXT NOT NULL',
               'status VARCHAR(80) NOT NULL',
               'comment TEXT',
                    ], ', ')

            stmt= """CREATE TABLE IF NOT EXISTS testactions (%s, PRIMARY KEY
            (testrun, tcid, title))""" % cols
            debug(stmt)
            c.execute(stmt)

    ##########################################################################
    def insertTestCase(self, tcDict, actionDicts= None):
        """
        inserts one new TestCase into the table(s)

        tcDict - Dictionary with tescase keys, values
        actionDicts - List of dictionaries with action keys, values
            tcid can be left.

        returns new testcase id
        """
        debug('DbLite.insertTestCase()')
        
        @with_transaction(self.env)
        def _insertTestCase(db):
            c= db.cursor()

            # constructs a statement of form "... VALUES (%s,%s,%s,%s)"
            # w/o autovalue tcid
            stmt= "INSERT INTO testcases (%s) VALUES (%s)" % (
                    string.join(TC_KEYS[1:], ',') , 
                    getInsertPlaceHolders(TC_KEYS[1:]))
            debug(stmt)
            
            c.execute(stmt, orderedValues(TC_KEYS[1:], tcDict))
            tcid= c.lastrowid
            debug("tcid= %d" % tcid)

            if (actionDicts):
                for ad in actionDicts: ad['tcid']= tcid

                # constructs a statement of form "... VALUES (%s,%s,%s,%s)"
                stmt= "INSERT INTO testactions (%s) VALUES (%s)" % (
                    string.join(TA_KEYS, ',') , 
                    getInsertPlaceHolders(TA_KEYS))
                debug(stmt)
                
                # build list from action value lists
                actions= []
                for d in actionDicts:
                    actions.append( orderedValues(TA_KEYS, d))

                # insert all actions in one step
                c.executemany(stmt, actions)

    ##########################################################################
    def getTestCaseCollumns(self):
        return TC_KEYS

    ##########################################################################
    def getTestCases(self, testrun= None, status= None):
        """
        selects all testcases of a given testrun with a given status.
        """
        debug('DbLite.getTestCases()')
        rows= []

        @with_transaction(self.env)
        def _getTestCases(db):
            c= db.cursor()
            
            # build filter
            filters= []
            fvalues= []
            if testrun: 
                filters.append( 'testrun=%s' )
                fvalues.append( testrun )
            if status: 
                filters.append( 'status=%s' )
                fvalues.append( status )

            # build statement
            stmt= "SELECT * FROM testcases"
            if filters:
                 stmt= stmt + ' WHERE ' + string.join( filters, ' AND ')
            
            debug( stmt )
            c.execute( stmt, fvalues )
            rows= c.fetchall()
            debug(rows)
            return rows
        return rows

    ##########################################################################
    def getTestActionCollumns(self):
        return TC_ACTIONS

    ##########################################################################
    def getTestActions(self, testrun= None, tcid= None, status= None):
        """
        Selects all testactions of a given testrun and testcase id with a given
        status.
        """
        debug('DbLite.getTestActions()')
        rows= []

        @with_transaction(self.env)
        def _getTestActions(db):
            c= db.cursor()
            
            # build filter
            filters= []
            fvalues= []
            if testrun: 
                filters.append( 'testrun=%s' )
                fvalues.append( testrun )
            if tcid: 
                filters.append( 'tcid=%s' )
                fvalues.append( tcid )
            if status: 
                filters.append( 'status=%s' )
                fvalues.append( status )

            # build statement
            stmt= "SELECT * FROM testactions"
            if filters:
                 stmt= stmt + ' WHERE ' + string.join( filters, ' AND ' )
            
            debug( stmt )
            c.execute( stmt, fvalues )
            rows= c.fetchall()
            debug(rows)
            return rows
        return rows

##############################################################################
if __name__ == "__main__":
    logging.basicConfig(
            level= logging.DEBUG, 
            #level= logging.INFO, 
            #format= "%(asctime)s %(levelname)s %(name)s %(message)s",
            #format= "%(asctime)s %(levelname)s %(name)s %(message)s",
            format= "%(message)s",
            #datefmt= "%Y-%m-%d %H:%M:%S",
            )
    import doctest
    doctest.testmod(optionflags= doctest.ELLIPSIS)

# vim: set ft=python ts=4 sw=4 expandtab :
