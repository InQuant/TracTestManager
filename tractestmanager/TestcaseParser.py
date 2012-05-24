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
        #setup_all(True)
        #create_all()

    def _parse_xml(self, version):
        # TODO: refactore the parsing of nodes...

        tree = Tree.fromstring(self.xml)
        # initial iteration
        # it is a Testcase
        case = TestCase()
        case.version = version
        try:
            case.wiki = self.pagename
        except Exception, e:
            ("This is only a dryrun")
        # we now have paragraph, paragraph and definition list
        # which represent "title", "description" and "actions"
        for node in tree:
            # set title and description
            if node.tag == 'paragraph':
                # TODO: if description has more paragraphs...
                if '=' in node.text:
                    case.title = node.text
                else:
                    case.description = node.text
            # now we have actions as definition list items
            else:
                for child in node.getchildren():
                    # every child has two children "term" and "definition"
                    # they are called action
                    ac = TestAction()
                    for action in child.getchildren():
                        if action.tag == 'definition':
                            # we have two paragraphs - action description and expected result
                            try:
                                actiondesc                  = action.getchildren()[0]
                                actionresult                = action.getchildren()[1]
                                ac.description              = self._build_markup(actiondesc)
                                ac.expected_result          = self._build_markup(actionresult)
                            except IndexError:
                                # TODO: %s - dinger rein
                                raise NoExpectedResult('No expected result set.')
                        else:
                            # append actiontitle to action
                            ac.title  = action.text
                    case.actions.append(ac)
        return case

    def _build_markup(self, node):
        # helperfunction to append additional markup tags
        # TODO: validate that text is built right
        nodemarkup = node.text
        for child in node.getchildren():
            if child.tag == 'title_reference':
                nodemarkup += child.text
        return nodemarkup

    def parseTestcase(self, pagename=None, text=None):
        # if we give a text - we only want to evaluate
        if text is not None:
            self.xml = publish_parts(text,writer_name = 'xml')['whole']
            return self._parse_xml(wikipage.version)
        else:
            # get the wiki page
            wikipage      = WikiPage(self.env, pagename)
            # get the xml representation of a testcase
            self.xml = publish_parts(wikipage.text,writer_name = 'xml')['whole']
            return self._parse_xml(wikipage.version)


class NoExpectedResult(Exception):
    pass

#   def __init__(self, message, errors):
#       Exception.__init__(self, message)
#       self.errors = "No expected result set"

# vim: set ft=python ts=4 sw=4 expandtab :
