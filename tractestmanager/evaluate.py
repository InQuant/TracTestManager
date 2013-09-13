# -*- coding: utf-8 -*-
#
# File: evaluate.py
#
# Copyright (c) Inquant GmbH
#

__author__ = 'Lutz Mende <lutz.mende@inquant.de>'
__docformat__ = 'plaintext'

import string

from trac.core import TracError

import db_models
from db_models import TA_TABLE, TA_KEYS, TC_TABLE, TC_KEYS
from db_models import SKIPPED, NOT_TESTED, PASSED, FAILED, PASSED_COMMENT
from config import get_display_states

import models
from models import TestCase, TestCaseQuery

def default_teststatus_groups():
    return [
        {
            'name': PASSED,
            'status': PASSED,
            'overall_completion': 'true',
            'css_class': 'passed',
            'statuses': set([PASSED]),
        },
        {
            'name': PASSED_COMMENT,
            'status': PASSED_COMMENT,
            'overall_completion': 'true',
            'css_class': 'passed_comment',
            'statuses': set([PASSED_COMMENT]),
        },
        {
            'name': FAILED,
            'status': FAILED,
            'css_class': 'failed',
            'statuses': set([FAILED]),
        },
        {
            'name': SKIPPED,
            'status': '*',
            'css_class': 'open',
            'statuses': set([SKIPPED, NOT_TESTED]),
        },
    ]

class TestCaseStatus(object):

    def __init__(self, env):
        self.env= env

    def get_testcase_stats( self, testcases ):
        return self.get_testcase_group_stats([tc.tcid for tc in testcases])

    def get_testcase_group_stats( self, tc_ids ):
        total_cnt = len(tc_ids)
        all_statuses = set(models.test_status())
        status_cnt = {}
        for s in all_statuses:
            status_cnt[s] = 0

        if total_cnt:
            db = self.env.get_db_cnx()
            cursor = db.cursor()
            str_ids = [str(x) for x in sorted(tc_ids)]
            cursor.execute("SELECT status, count(status) FROM testcase "
                           "WHERE tcid IN (%s) GROUP BY status" %
                           ",".join(str_ids))
            for s, cnt in cursor:
                status_cnt[s] = cnt

        stat = TestItemGroupStats('testcase status', 'testcases')

        groups =  default_teststatus_groups()

        display = get_display_states(self.env)
        for group in groups:
            group_cnt = 0
            query_args = {}
            for s, cnt in status_cnt.iteritems():
                if s in group['statuses']:
                    group_cnt += cnt
                    query_args.setdefault('status', []).append(display[s])
            for arg in [kv for kv in group.get('query_args', '').split(',')
                        if '=' in kv]:
                k, v = [a.strip() for a in arg.split('=', 1)]
                query_args.setdefault(k, []).append(v)
            group['label'] = display[group['name']]
            stat.add_interval(group.get('label', group['name']),
                              group_cnt, query_args,
                              group.get('css_class', group['name']),
                              bool(group.get('overall_completion')))
        stat.refresh_calcs()
        return stat

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

# vim: set ft=python ts=4 sw=4 expandtab :
