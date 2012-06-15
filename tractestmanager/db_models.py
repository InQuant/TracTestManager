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
TC_KEYS= [ 'tcid', 'wiki', 'title', 'description', 'revision', 'tester', 'testrun', 'status']
# TestAction collumns
TA_KEYS= [ 'id', 'tcid', 'testrun', 'title', 'description', 'expected_result', 'status', 'comment']

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
    >>> env= Environment( '/Users/lmende/develop/tractestman/buildout/parts/trac' )
    
    1. Instanciate the class and set it up aka create the tables.

    >>> db= DbLite(env)

    2. Build a dict for a Testcase to add.


    >>> tcvals= ['TcDocCreate', 'Create Docs', 'bla', '2', 'lmende', 3, NOT_TESTED]

    3. Build a list of dicts for TestActions to add.

    >>> vals1= [ 3, 'Add to Workspace', 'Add to WS desc', 'Docs added',PASSED, None ]
    >>> vals2= [ 3, 'Checkout', 'Checkout desc', 'Docs checked out', NOT_TESTED, None ]
    >>> actions= [dict(zip(TA_KEYS[2:], vals1)), dict(zip(TA_KEYS[2:], vals2))]
    
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
    def __init__(self, env):
        debug('DbLite.__init__()')
        self.env= env

    ##########################################################################
    def setup(self):
        """
        Sets up the two additional testman tables
        """
        debug('DbLite.setup()')


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
            stmt= "INSERT INTO testcase (%s) VALUES (%s)" % (
                    string.join(TC_KEYS[1:], ',') , 
                    getInsertPlaceHolders(TC_KEYS[1:]))
            debug(stmt)
            
            c.execute(stmt, orderedValues(TC_KEYS[1:], tcDict))
            tcid= c.lastrowid
            debug("tcid= %d" % tcid)

            if (actionDicts):
                for ad in actionDicts: ad['tcid']= tcid

                # constructs a statement of form "... VALUES (%s,%s,%s,%s)"
                stmt= "INSERT INTO testaction (%s) VALUES (%s)" % (
                    string.join(TA_KEYS[1:], ',') , 
                    getInsertPlaceHolders(TA_KEYS[1:]))
                debug(stmt)
                
                # build list from action value lists
                actions= []
                for d in actionDicts:
                    actions.append( orderedValues(TA_KEYS[1:], d))

                # insert all actions in one step
                c.executemany(stmt, actions)

    ##########################################################################
    def getTestCaseCollumns(self):
        return TC_KEYS

    ##########################################################################
    def getTestCases(self, tcid= None, testrun= None, tester= None, status= None):
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
            if tcid: 
                filters.append( 'tcid=%s' )
                fvalues.append( tcid )
            if testrun: 
                filters.append( 'testrun=%s' )
                fvalues.append( testrun )
            if tester: 
                filters.append( 'tester=%s' )
                fvalues.append( tester )
            if status: 
                filters.append( 'status=%s' )
                fvalues.append( status )

            # build statement
            stmt= "SELECT * FROM testcase"
            if filters:
                 stmt= stmt + ' WHERE ' + string.join( filters, ' AND ')
            
            debug( filters )
            debug( fvalues )
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
    def getTestActions(self, id= None, tcid= None, testrun= None, status= None):
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
            if id: 
                filters.append( 'id=%s' )
                fvalues.append( id )
            if tcid: 
                filters.append( 'tcid=%s' )
                fvalues.append( tcid )
            if testrun: 
                filters.append( 'testrun=%s' )
                fvalues.append( testrun )
            if status: 
                filters.append( 'status=%s' )
                fvalues.append( status )

            # build statement
            stmt= "SELECT * FROM testaction"
            if filters:
                 stmt= stmt + ' WHERE ' + string.join( filters, ' AND ' )
            
            debug( filters )
            debug( fvalues )
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
