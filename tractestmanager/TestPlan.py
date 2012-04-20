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
        conf, testcases = self.parse_config(text)
        #markupreturn = 'TestPlan, text = %s, args = %s' % \
            #(Markup.escape(text), Markup.escape(repr(args)))
        #wikisite = '== Executing wiki macros =='
        text = self._build_configs_wiki(conf)
        text += self._build_testcases_wiki(testcases)
        out = StringIO.StringIO()
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
        print testcases
        return attributes, testcases

    def get_wiki_page(self,path):
        # put some information about a wiki page that has been selected
        print "getting wiki page for \"" + path + "\"..."
        pass

    def _build_configs_wiki(self,config):
        """ builds wiki formatting for the configuration table
        """
        text = "== Konfigurierte Parameter ==\n||'''Attribut'''||'''Wert'''||\n"
        table = ''
        for key in config.keys():
            table += '||%s||%s||\n' % (key, config[key])
        return text + table

    def _build_testcases_wiki(self, testcases):
        text = "\n== Testcases ==\n||'''Testcase'''||'''User'''||\n"
        for testcase in testcases:
            for key in testcase:
                text += '||%s||%s||\n' % (key, testcase[key])
        return text

# vim: set ft=python ts=4 sw=4 expandtab :
