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
from models import *

class TestcaseParser(object):
    """ Testcase parser class
    """
    def __init__(self, env):
        self.env   = env
        setup_all(True)
        create_all()

    def _parse_xml(self):
        tree = Tree.fromstring(self.xml)
        # initial iteration
        # it is a Testcase
        case = Testcase()
        case.wiki = self.pagename
        # we now have paragraph, paragraph and definition list
        # which represent "title", "description" and "actions"
        for node in tree:
            # set title and description
            if node.tag == 'paragraph':
                if '=' in node.text:
                    case.title = node.text
                else:
                    case.desc = node.text
            # now we have actions as definition list items
            else:
                for child in node.getchildren():
                    # every child has two children "term" and "definition"
                    # they are called action
                    ac = Testaction()
                    for action in child.getchildren():
                        if action.tag == 'definition':
                            # we have two paragraphs - action description and expected result
                            # XXX: Failure Handling
                            try:
                                actiondesc          = action.getchildren()[0]
                                actionresult        = action.getchildren()[1]
                                ac.description      = self._build_markup(actiondesc)
                                ac.expected_result  = self._build_markup(actionresult)
                            except Exception, e:
                                ac.desc      = self._build_markup(actiondesc)
                                ac.result    = "no expected result available"
                        else:
                            # append actiontitle to action
                            ac.title  = action.text
                    case.actions.append(ac)
        #session.commit()
        return case

    def _build_markup(self, node):
        # helperfunction to append additional markup tags
        # TODO: validate that text is built right
        nodemarkup = node.text
        for child in node.getchildren():
            if child.tag == 'title_reference':
                nodemarkup += child.text
        return nodemarkup

    def parseTestcase(self, pagename):
        # get the wiki page
        wikipage      = self._get_page(pagename)
        # get the xml representation of a testcase
        self.xml = publish_parts(wikipage.text,writer_name = 'xml')['whole']
        return self._parse_xml()

    def _get_page(self, pagename):
        try:
            self.pagename = pagename
            wikipage = WikiPage(self.env, pagename)
            self.wikipage = wikipage
        except Exception, e:
            print 'Page %s not found.' % (pagename)
            wikipage = None
        return wikipage
