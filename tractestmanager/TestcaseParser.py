# -*- coding: utf-8 -*-
#
# File: TestPlan.py
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

__author__ = 'Otto Hockel <otto.hockel@inquant.de>'
__docformat__ = 'plaintext'

from trac.wiki import WikiPage
from docutils.core import publish_parts
import xml.etree.ElementTree as Tree

class TestcaseParser:
    """Model class for Testcases
    """
    def __init__(self,env):
        self.env = env

    def _get_page(self,pagename):
        try:
            wikipage = WikiPage(self.env, pagename)
        except Exception, e:
            print 'Page %s not found.' % (pagename)
            wikipage = None
        return wikipage

    def parseTestcase(self,pagename):
        wikipage = self._get_page(pagename)
        document = publish_parts(wikipage.text,writer_name = 'xml')
        testcase = self._parse_xml(document)

        return None

    def _parse_xml(self,document):
        tree = Tree.fromstring(document['whole'])
        for node in tree:
            print node
        return tree

