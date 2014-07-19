# -*- coding: utf-8 -*-
#
# File: config.py
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

from testmanconst import PASSED, PASSED_COMMENT, FAILED, SKIPPED, NOT_TESTED
from utils import reverse_dict

MANAGER_PERMISSION = 'TM_TESTMANAGER'
TESTER_PERMISSION = 'TM_TESTER'

STATES_DISPLAY = {
    PASSED: u'passed',
    PASSED_COMMENT: u"passed_comment",
    FAILED: u'failed',
    SKIPPED: u'skipped',
    NOT_TESTED: u'not_tested'
}


def get_display_states(component):
    """ get configured display states from trac.ini if configured
    [testmanager]
    passed = foo
    passed_comment = bar
    failed = doh
    skipped = n
    not_tested = -
    """
    states = dict(
        [option for option in component.config.options('testmanager')]
    )
    if not states or not len(states) == len(STATES_DISPLAY):
        return reverse_dict(STATES_DISPLAY)
    return states

