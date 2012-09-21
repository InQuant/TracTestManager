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
from trac.core import TracError
from trac.wiki import WikiSystem

from docutils.core import publish_doctree
from docutils.nodes import SkipChildren, SkipSiblings

from models import TestCase
from models import TestAction
from TestManagerLib import safe_unicode

import re

class TestcaseParser(object):
    """ parses a testcase in wiki format
    """
    def __init__(self, env):
        self.env   = env
        self.dbg   = env.log.debug

    def parseTestcase(self, pagename= None, text= None):
        self.dbg('TestcaseParser.parseTestcase( %s, %s )' % (pagename, text))

        if pagename:
            # get the text from the given wiki page
            wikipage= WikiPage(self.env, pagename)
            text= wikipage.text
            version= wikipage.version
        else:
            # text must be given for syntax check
            version= None

        xmltree = publish_doctree(text)
        case = self._parse_xml(xmltree, pagename, version)

        return case

    def _parse_xml(self, xmltree, pagename= None, version= None):
        self.dbg('TestcaseParser._parse_xml( %s, %s )' % (pagename, version))

        # it is a Testcase
        case = TestCase(self.env)
        case.version = version
        case.wiki = pagename
        case.description= ""

        # we now have paragraph, paragraph and definition list
        # which represent "title", "description" and "actions"
        for node in xmltree:

            if node.tagname not in ['paragraph', 'block_quote']:
                self.dbg('ignored: %s' % node.shortrepr())
                continue

            # set title or description
            if node.tagname == 'paragraph':
                text= self._node_text(node)

                if '=' in text:
                    self.dbg('set title: %s' % node.shortrepr())
                    case.title = text
                else:
                    # TODO - save the pararagraph or linefeed
                    self.dbg('append description: %s' % node.shortrepr())
                    case.description += text

            else:
                # we have a block_quote which can be lists

                for child in node.children:

                    if child.tagname == 'definition_list':
                        # a definition list contains our actions
                        self._parse_deflist( case, child )
                    else:
                        # all the rest will be interpreted as description
                        self.dbg('append description: %s' % child.shortrepr())
                        case.description += self._node_text(child)

        self.dbg( "case: %s" % case.getattrs() )

        # check testcase
        if not case.title:
            raise TracError( safe_unicode(
                'Testcase title is missing, please fix: %s' % xmltree.astext()[:256]))

        if len(case.actions) == 0:
            raise TracError( safe_unicode(
                'Testcase actions are missing, please add actions for: "%s"' %
                case.title))

        return case

    def _parse_deflist( self, case, node ):
        self.dbg('TestcaseParser._parse_deflist( %s )' % node.shortrepr())
        for child in node.children:

            if child.tagname != 'definition_list_item':
                self.dbg('ignored: %s' % child.shortrepr())
                continue

            ta= self._parse_deflist_item( child )

            for key in ['title', 'description', 'expected_result']:
                if not ta[key]:
                    raise TracError( safe_unicode(
                        'Action definition incomplete (%s missing!), please fix! Near line %s: %s' %
                        (key, child.line, child.astext())))
                self.dbg( "action %s: %s" % (key, ta[key]) )

            case.add_action( ta )

    def _parse_deflist_item( self, node ):
        self.dbg('TestcaseParser._parse_deflist_item( %s )' % node.shortrepr())

        ta= TestAction( self.env )
        for child in node.children:

            if child.tagname not in ['term', 'definition',]:
                self.dbg('ignored: %s' % child.shortrepr())
                continue

            if child.tagname == 'term':
                # term is the action title
                text= self._node_text(child).strip(':')
                self.dbg('set action title: %s' % text)
                ta.title= text

            if child.tagname == 'definition':
                self._parse_definition( ta, child )

        return ta

    def _parse_definition( self, taction, node ):
        self.dbg('TestcaseParser._parse_definition( %s )' % node.shortrepr())

        description_set= False
        for child in node.children:

            if child.tagname not in ['paragraph', 'block_quote',]:
                self.dbg('ignored: %s' % child.shortrepr())
                continue

            # action description
            if not description_set:
                text= self._node_text(child)
                self.dbg('set action description: %s' % text)
                taction.description= text
                description_set= True

            # action result
            else:
                text= self._node_text(child)
                self.dbg('set action result: %s' % text)
                taction.expected_result= text
                break

    def _node_text( self, node ):
        if node.rawsource:
            return node.rawsource
        else:
            return node.astext()

class TestPlanMacroParser(object):

    def __init__(self, env):
        self.env= env
        self.dbg= env.log.debug

    def parse_config(self, text):
        """Parses the macro configuration parameters
           returns a dictionary of attributes
        """
        self.dbg( 'TestPlanMacroParser.parse_config' )
        attributes = dict()
        tcpats_and_users = list()
        lines = text.splitlines()
        # parse attributes
        for line in lines:
            line= line.strip()

            # skip empty lines
            if not line: continue

            # this is a test parameter
            if ':' in line:
                x,y = line.split(':')
                x = x.lower().strip()
                attributes[x] = y.strip()

            # otherwise it should be a testcase line
            else:
                users= list()
                try:
                    tcpattern, rest= line.split(None, 1)
                    # more than one user given?
                    users= rest.split()
                except ValueError:
                    tcpattern= line.strip()
                    users= ['',]

                tcpats_and_users.append( [tcpattern.strip(), users,] )

                # eval the wildcard testcase names
                tcnames_and_users= self._eval_wildcards(tcpats_and_users)

        return attributes, tcnames_and_users

    def _get_wiki_pages(self,prefix):
        """ wrap the wiki api
        """
        for page in WikiSystem(self.env).get_pages(prefix):
            yield page

    def _eval_wildcards(self, tcpats_and_users):
        """ take the testcasepattern - user tuples, eval the wildcard pattern

            e.g. ( 'TestMan*', ['max', 'muster', ])
        """
        self.dbg( 'TestPlanMacroParser._eval_wildcards: %s' % tcpats_and_users )

        tcnames_and_users = dict()

        for tcpat, users in tcpats_and_users:
            if '*' in tcpat:
                wildcard = tcpat.rstrip('*')
                for title in self._get_wiki_pages(wildcard):
                    tcnames_and_users[title] = users
            else:
                tcnames_and_users[tcpat] = users

        self.dbg( 'tcnames_and_users: %s' % tcnames_and_users )
        return tcnames_and_users

# vim: set ft=python ts=4 sw=4 expandtab :
