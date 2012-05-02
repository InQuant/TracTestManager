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
#from models import *

class TestcaseParser:
    """Model class for Testcases
    """
    def __init__(self,env):
        self.env   = env
        ##setup_all(True)
        ##create_all()
        self.title = ''
        self.desc  = ''
        self.steps = list()

    def _get_page(self,pagename):
        try:
            wikipage = WikiPage(self.env, pagename)
            self.wikipage = wikipage
        except Exception, e:
            print 'Page %s not found.' % (pagename)
            wikipage = None
        return wikipage

    def _parse_xml(self,document):
        tree = Tree.fromstring(document['whole'])
        # initial iteration
        # it is a Testcase
        ##case = Testcase()
        ##case.wiki = self.wikipage
        # we now have paragraph, paragraph and definition list
        # which represent "title", "description" and "actions"
        for node in tree:
            # set title and description
            if node.tag == 'paragraph':
                if '=' in node.text:
                    self.title = node.text
                    ##case.title = node.text
                else:
                    self.desc = node.text
                    ##case.desc = node.text
            # now we have actions as definition list items
            else:
                for child in node.getchildren():
                    # every child has two children "term" and "definition"
                    # they are called action
                    ##ac = Action()
                    for action in child.getchildren():
                        if action.tag == 'definition':
                            # we have two paragraphs - action description and expected result
                            actiondesc, actionresult = action.getchildren()
                            ##ac.desc   = actiondesc.text
                            ##ac.result = actionresult.text
                            print "action desc  : " + actiondesc.text
                            print "action result: " + actionresult.text
                        else:
                            # append steptitle to steps
                            ##ac.title  = action.text
                            print "action title : " + action.text
                    ##case.actions.append(ac)
        ##session.commit()
        return tree

    def parseTestcase(self,pagename):
        wikipage = self._get_page(pagename)
        document = publish_parts(wikipage.text,writer_name = 'xml')
        testcase = self._parse_xml(document)

        return None
