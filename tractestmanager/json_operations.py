
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
        id = req.args.get("action", None)
        status = req.args.get("status", None)
        comment = req.args.get("comment", "")
        runid = req.args.get("testrun", None)
        try:
            testaction = models.TestActionQuery(self.env, id=id).execute()[0]
            if comment:
                testaction.set_status(status=status, comment=comment)
                testrun = Ticket(self.env, tkt_id=runid)
                # add comment to ticket with ta_id, comment and tcid
                testcase = models.TestCaseQuery(self.env, tcid=testaction.tcid).execute()[0]
                # TODO: check if testcase can be opened from a ticket
                tc_link = "[%s/TestManager/general/testcase/%s TestCase #%s]" % (req.abs_href(), testaction.tcid, testaction.tcid)
                comment_data = {"title": testaction.title,
                        "ta_id" : id,
                        "status" : status,
                        "wiki": testcase.wiki,
                        "revision": testcase.revision,
                        "tc_link": tc_link,
                        "comment": comment}
                comment = COMMENT_TEMPLATE % comment_data
                # TODO: decode base64
                testrun.save_changes(author=req.authname, comment=comment)
            # send ajax callback success
            else:
                testaction.set_status(status=status, comment=None)
            req.send(json.dumps({"update":"success", "status":status}))
        except TracError:
                # TODO: use callback to render errors
                req.send(json.dumps({"update":"failed"}))

# vim: set ft=python ts=4 sw=4 expandtab :
