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
        self.env   = env
        self.title = ''
        self.desc  = ''
        self.steps = list()

    def _get_page(self,pagename):
        try:
            wikipage = WikiPage(self.env, pagename)
        except Exception, e:
            print 'Page %s not found.' % (pagename)
            wikipage = None
        return wikipage

    def _parse_xml(self,document):
        tree = Tree.fromstring(document['whole'])
        # initial iteration
        # we now have paragraph, paragraph and definition list
        # which represent "title", "description" and "steps"
        for node in tree:
            # set title and description
            if node.tag == 'paragraph':
                if '=' in node.text:
                    self.title = node.text
                else:
                    self.desc = node.text
            # now we have steps as definition list items
            else:
                for child in node.getchildren():
                    # every child has two children "term" and "definition"
                    # they are called action
                    print child.getchildren()
                    for action in child.getchildren():
                        # append steptitle to steps
                        if action.tag == 'term':
                            pass

        return tree

    def parseTestcase(self,pagename):
        wikipage = self._get_page(pagename)
        document = publish_parts(wikipage.text,writer_name = 'xml')
        testcase = self._parse_xml(document)

        return None
