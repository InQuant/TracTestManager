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

from genshi.core import Markup

from trac.wiki.macros import WikiMacroBase
from trac.wiki import Formatter
from trac.wiki import WikiSystem
import StringIO

class TestPlanMacro(WikiMacroBase):
    """Testplan macro.
       Formats a Wiki Testplan.
       Usage::

           {{{
           #!TestPlan
           Id: TA14
           Testart: UsecaseTest 
           Build: DC-3.1.1
           Konfiguration: IE7-Win, FF-LUX
           Usecases: BaugruppenVerwalten, ObjekteSuchen

           Testcases/SaveAsEinerBaugruppe lmende
           Testcases/ErzeugenEinerBaugruppe lmende
           Testcases/Suchen/* mmuster
           }}}
    """

    revision = "$Rev$"
    url = "$URL$"

    def expand_macro(self, formatter, name, text, args):
        """Execute the macro
        """
        from TestcaseParser import TestcaseParser
        case = TestcaseParser(self.env)
        wikipage = case.parseTestcase("Testcases/UC011")
        # Parse config and testcases
        conf, testcases = self.parse_config(text)
        # Build config params in wiki syntax
        text = self._build_configs_wiki(conf)
        # Build testcases in wiki syntax
        testcases = self._build_testcases_wiki(testcases)
        text += testcases
        out = StringIO.StringIO()
        # TODO: Escape wiki markup for text
        Formatter(self.env, formatter.context).format(text,out)
        return Markup(out.getvalue())

    def parse_config(self, text):
        """Parses the macro configuration parameters
           returns a dictionary of attributes
        """
        attributes = dict()
        testcases = list()
        lines = text.splitlines()
        # parse attributes
        for line in lines:
            if ':' in line:
                line.replace(' ','')
                x,y = line.split(':')
                attributes[x] = y
            if '/' in line:
                testcasepath, user = line.split()
                testcases.append({testcasepath:user})
        return attributes, testcases

    def _build_configs_wiki(self,config):
        """ builds wiki formatting for the configuration table
        """
        text = "== Testparameter ==\n||'''Attribut'''||'''Wert'''||\n"
        table = ''
        for key in config.keys():
            table += '||%s||%s||\n' % (key, config[key])
        return text + table

    def _build_testcases_wiki(self, testcases):
        """ builds the testcases in wiki syntax
            returns wikitext
        """
        text = "\n== Zu testende Testcases ==\n||'''Testcase'''||'''User'''||\n"
        for testcase in testcases:
            for key in testcase:
                path = key.split('*')[0]
                path = path.rstrip('/')
                for title in self._get_wiki_pages(path):
                    text += '||%s||%s||\n' % (title, testcase[key])
        return text

    def _get_wiki_pages(self,prefix):
        """ wrap the wiki api
        """
        for page in WikiSystem(self.env).get_pages(prefix):
            yield page

# vim: set ft=python ts=4 sw=4 expandtab :
