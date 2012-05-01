# -*- coding: utf-8 -*-
#
# File: web_ui.py
#
# Copyright (c) Inquant GmbH
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

import re
import math
from trac.core import *
from trac.web.api import IRequestHandler
from trac.web.chrome import ITemplateProvider, INavigationContributor, \
                            add_stylesheet, add_ctxtnav
from genshi.builder import tag as builder
from trac.util import to_unicode
from trac.util.compat import sorted, set, any
from tractags.api import TagSystem, ITagProvider
#from tractags.query import InvalidQuery
from trac.resource import Resource
from trac.mimeview import Context
from trac.wiki.formatter import Formatter


class TagTemplateProvider(Component):
    """Provides templates and static resources for the Testmanager plugin."""

    implements(ITemplateProvider)

    # ITemplateProvider methods
    def get_templates_dirs(self):
        """
        Return the absolute path of the directory containing the provided
        ClearSilver templates.
        """
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        """Return the absolute path of a directory containing additional
        static resources (such as images, style sheets, etc).
        """
        from pkg_resources import resource_filename
        return [('testmanager', resource_filename(__name__, 'htdocs'))]


class TagRequestHandler(Component):
    """Implements the /testmanager handler (i.e. the Menu)."""

    implements(IRequestHandler, INavigationContributor)

    tag_providers = ExtensionPoint(ITagProvider)

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        if 'TAGS_VIEW' in req.perm:
            return 'testmanager'

    def get_navigation_items(self, req):
        if 'TAGS_VIEW' in req.perm:
            yield ('mainnav', 'testmanager',
                   builder.a('Testmanager', href=req.href.testmanager(), accesskey='T'))

    # IRequestHandler methods
    def match_request(self, req):
        return 'TAGS_VIEW' in req.perm and req.path_info.startswith('/testmanager')
        
    def process_request(self, req):
        data = {'title': 'Testmanager'}
        add_stylesheet(req, 'testmanager/css/testmanager.css')
        return 'testmanager.html', data, None
