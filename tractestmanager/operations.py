
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

#from trac.util.compat import partial

#from trac.perm import IPermissionRequestor
#from trac.perm import PermissionError

# testman specific imports
#from config import MANAGER_PERMISSION, TESTER_PERMISSION

import json
#import db_models
import models

class TestCaseManipulator(Component):
    """ Component that supports the Testcase Execution
    """
    implements(IRequestHandler)

    # XXX: This is a hack - refactor later
    #      every request with /json_operate/? in it will match
    def match_request(self, req):
        return re.match(r'/json_testaction/?', req.path_info) is not None

    def process_request(self, req):
        try:
            # mocking testaction set ok
            testaction = models.TestActionFilter().get(ta_id=req.args['ta_id'])[0]
            testaction.set_status(**req.args)
            req.send(json.dumps({"STATUS_UPDATE":"SUCCESS"}))
        except TracError, e:
            raise TracError(e)

# vim: set ft=python ts=4 sw=4 expandtab :
