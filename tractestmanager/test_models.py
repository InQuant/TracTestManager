# -*- coding: utf-8 -*-
#
# File: models.py
#
# Copyright (c) Inquant GmbH
#

__author__ = 'Lutz Mende <lutz.mende@inquant.de>'
__docformat__ = 'plaintext'

import os
import unittest
import string

from trac.env import Environment

import db_models
from db_models import TA_TABLE, TA_KEYS, TC_TABLE, TC_KEYS
from db_models import NOT_TESTED, PASSED, FAILED, PASSED_COMMENT
from models import TestCase, TestAction

# TC_KEYS= [ 'tcid', 'wiki', 'title', 'description', 'revision', 'tester', 'testrun', 'status']
# TA_KEYS= [ 'id', 'tcid', 'testrun', 'title', 'description', 'expected_result', 'status', 'comment']

class TestCaseTestCase(unittest.TestCase):

    def setUp(self):
        self.env= Environment( '/Users/lmende/develop/tractestman/buildout/parts/trac' )

        self.tcvals= ['TcDocCreate', 'Create Docs', 'bla', '2', 'lmende', 3, NOT_TESTED]

        avals1= [ 3, 'Add to Workspace', 'Add to WS desc', 'Docs added',NOT_TESTED, None ]
        avals2= [ 3, 'Checkout', 'Checkout desc', 'Docs checked out', NOT_TESTED, None ]
        self.acdicts= [dict(zip(TA_KEYS[2:], avals1)), dict(zip(TA_KEYS[2:], avals2))]

    def tearDown(self):
        pass

    def test_create(self):

        tc= TestCase( self.env, dict(zip(TC_KEYS[1:], self.tcvals)) )
        for a in self.acdicts:
            tc.add_action( TestAction( self.env, a ))

        for k, v in zip(TC_KEYS[1:], self.tcvals):
            self.assertEqual(v, tc[k])


        self.assertEqual(2, len(tc.actions))

    def test_insert(self):
        tc= TestCase( self.env, dict(zip(TC_KEYS[1:], self.tcvals)) )
        for a in self.acdicts:
            tc.add_action( TestAction( self.env, a ))
        self.assertTrue(tc.insert() is not None)

    def test_set_status(self):
        tc= TestCase( self.env, dict(zip(TC_KEYS[1:], self.tcvals)) )
        for a in self.acdicts:
            tc.add_action( TestAction( self.env, a ))
        tc.insert()

        for a in tc.actions:
            a.set_status(FAILED, 'dat war wohl nix')
        tc.set_status(FAILED)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCaseTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

# vim: set ft=python ts=4 sw=4 expandtab :
