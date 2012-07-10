# -*- coding: utf-8 -*-
#
# File: db_models.py - wraps the trac sql stuff needed in testman
#
# Copyright (c) Inquant GmbH
#

__author__ = 'Lutz Mende <lutz.mende@inquant.de>'
__docformat__ = 'plaintext'

# (case | action) status
NOT_TESTED= 'not tested'
PASSED= 'passed'
PASSED_COMMENT= 'passed with comment'
FAILED= 'failed'
SKIPPED= 'skipped'

# TestCase collumns
TC_TABLE= 'testcase'
TC_KEYS= [ 'tcid', 'wiki', 'title', 'description', 'revision', 'tester', 'testrun', 'status']

# TestAction collumns
TA_TABLE= 'testaction'
TA_KEYS= [ 'id', 'tcid', 'testrun', 'title', 'description', 'expected_result', 'status', 'comment']
