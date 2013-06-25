
# -*- coding: utf-8 -*-
#
# File: __init__.py
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

__author__ = 'Otto Hockel <hockel.otto@inquant.de.com>'
__docformat__ = 'plaintext'

import re
from trac.core import Component
#from trac.core import ExtensionPoint
from trac.core import implements
from trac.core import TracError
from trac.ticket.query import Query

from trac.web import IRequestHandler

from datetime import datetime
from trac.util.datefmt import utc

#from genshi.builder import tag
#from trac.util.compat import partial

#from trac.perm import IPermissionRequestor
#from trac.perm import PermissionError

# testman specific imports
#from config import MANAGER_PERMISSION, TESTER_PERMISSION

import json
from trac.ticket.model import Ticket
import models

COMMENT_TEMPLATE = """
%(status)s "%(title)s" in %(tc_link)s for [wiki:%(wiki)s?revision=%(revision)s&ta_id=%(ta_id)s]

%(comment)s
"""

class TestCaseManipulator(Component):
    """ Component that supports the Testcase Execution
    """
    implements(IRequestHandler)

    # XXX: This is a hack - refactor later
    #      every request with /json_testaction/? in it will match
    #      how a to define a valid operation:
    #      http://localhorst:8000/trac/json_testaction?user=testuser&id=1&status=failed&comment=fooobar&testrun=1
    def match_request(self, req):
        return re.match(r'/json_testaction', req.path_info) is not None

    def process_request(self, req):
        self.dbg= self.env.log.debug

        toggle_container_id = req.args.get("toggle_container_id", None)

        id      = req.args.get("action", None)
        status  = req.args.get("status", None)
        comment = req.args.get("comment", "")
        option  = req.args.get("option", None)
        runid   = req.args.get("testrun", None)

        json_response = {
                'update' : 'success',
                'status' : status,
                'toggle_container_id' : toggle_container_id
                }

        try:
            testaction = models.TestActionQuery(self.env, id=id).execute()[0]

            if option == "create_ticket":
                if not comment:
                    raise AttributeError("For ticket creation a comment is mandatory!")
                if status == 'skipped':
                    raise AttributeError("Status 'skipped' is not allowed for ticket creation!")

            if option == "attach_file":
                if not comment:
                    raise AttributeError("For attachment creation a comment is mandatory!")
                if status == 'skipped':
                    raise AttributeError("Status 'skipped' is not allowed for attachment creation!")

            if comment:
                if comment == testaction.comment:
                    raise AttributeError("Same comment was saved already.")
                testaction.set_status(status=status, comment=comment, tester=req.authname)

                if option == "create_ticket":
                    tid= self._create_ticket( runid, testaction, comment, req )
                    comment= "%s\n\nSee ticket #%-d." % (comment, tid)

                json_response['cnum'] = self._add_comment_to_testrun( runid, testaction, comment, req )

            else:
                testaction.set_status(status=status, comment=None, tester=req.authname)

            # send ajax callback success
            req.send(json.dumps(json_response))
        except (AttributeError, TracError) , e:
            req.send(json.dumps({"update":"failed", "message":unicode(e)}), status=500)

    def _create_ticket(self, runid, testaction, comment, req):
        """ creates a ticket for an action (defect if failed, enhancement if
        passed)

        """
        self.dbg('accordion.request._create_ticket(%s)' % req.args)

        testrun = Ticket(self.env, tkt_id=runid)

        # determine type of ticket
        ticket_type= 'defect'
        todo= 'failed'
        if testaction.status != 'failed':
            ticket_type= 'enhancement'
            todo= 'is unreasonable'

        # build ticket summary: <todo>: <action> of <testcase>, e.g.:
        # 'Creator checks in the model of TcCaddocCreate failed.'
        testcase = models.TestCaseQuery(self.env, tcid=testaction.tcid).execute()[0]
        summary= "%s of %s %s." % (testaction.title, testcase.wiki, todo)

        # check if a similar ticket already exists...
        existing_tickets= Query.from_string(self.env, "summary=%s" % summary).execute()
        if existing_tickets:
            # TODO: add the comment to existing ticket

            # if yes return the ticket id
            return existing_tickets[0]['id']

        # build description
        description= "Related test case: %s.\n\n%s" % (self._build_tc_link(testaction, req), comment)

        # build the ticket
        ticket = Ticket(self.env)
        data = {
            'reporter'     : req.authname,
            'summary'      : summary,
            'type'         : ticket_type,
            'description'  : description,
            'priority'     : req.args.get('priority', 'major'),
            'keywords'     : self._get_testplan_title( testrun ),
        }
        self.dbg('ticket data: %s' % data)

        try:
            ticket.populate(data)
            tid = ticket.insert()
            ticket.save_changes()

        except TracError, e:
            self.env.log.error(e)
            raise TracError( safe_unicode("ticket could not be created: %s" %
                    e.message ))

        return tid

    def _get_testplan_title(self, testrun):
        """ parses the testplan title out of testrun ticket description.

            e.g.
            = [wiki:TestplanDemo] =
        """
        pat= re.compile( "\[wiki:(.*?)\]" )
        m= pat.search( testrun['description'] )
        if m:
            return m.group(1)
        else:
            return ""

    def _build_tc_link(self, testaction, req):
        return "[%s/TestManager/general/testcase/%s TestCase #%s]" % (req.abs_href(),
                testaction.tcid, testaction.tcid)

    def _add_comment_to_testrun(self, runid, testaction, comment, req):

        id= testaction.id
        testrun = Ticket(self.env, tkt_id=runid)

        # add comment to ticket with ta_id, comment and tcid
        testcase = models.TestCaseQuery(self.env, tcid=testaction.tcid).execute()[0]
        # TODO: check if testcase can be opened from a ticket
        tc_link = self._build_tc_link( testaction, req)
        comment_data = {"title": testaction.title,
                "ta_id" : id,
                "status" : testaction.status,
                "wiki": testcase.wiki,
                "revision": testcase.revision,
                "tc_link": tc_link,
                "comment": comment}
        comment = COMMENT_TEMPLATE % comment_data
        # TODO: decode base64
        return testrun.save_changes(author= req.authname, comment=comment)

# vim: set ft=python ts=4 sw=4 expandtab :
