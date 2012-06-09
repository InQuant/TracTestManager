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

from trac.core import TracError
from trac.wiki.formatter import system_message
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
        parser = TestcaseParser(self.env)
        errors = list()
        #wikipage = case.parseTestcase("Testcases/UC011")
        # Parse config and testcases
        conf, testcases = self.parse_config(text)
        for key in testcases:
            try:
                parser.parseTestcase(key)
            except TracError, e:
                error_message = "Parsing error in Testcase %s:" % key
                errors.append(system_message(error_message, text=e.message))
        # Build config params in wiki syntax
        text = self._build_configs_wiki(conf)
        # Build testcases in wiki syntax
        testcases = self._build_testcases_wiki(testcases)
        text += testcases
        out = StringIO.StringIO()
        # TODO: Escape wiki markup for text
        Formatter(self.env, formatter.context).format(text,out)
        for e in errors:
            out.write(e)
        return Markup(out.getvalue())

    def parse_config(self, text):
        """Parses the macro configuration parameters
           returns a dictionary of attributes
        """
        attributes = dict()
        caselines  = dict()
        lines = text.splitlines()
        # parse attributes
        for line in lines:
            # this is a test parameter
            if ':' in line:
                line.replace(' ','')
                x,y = line.split(':')
                x = x.lower()
                attributes[x] = y
            # and this a testcase markup
            if '/' in line:
                testcasepath, user = line.split()
                caselines[testcasepath] = user
                testcases = self._parse_testcasemarkup(caselines)
        return attributes, testcases

    def _get_wiki_pages(self,prefix):
        """ wrap the wiki api
        """
        for page in WikiSystem(self.env).get_pages(prefix):
            yield page

    def _parse_testcasemarkup(self, markup):
        """ take the 'Testcases/*' syntax and get all uc for them
            return a dict with a pagename and the user
            {'Testcases/UC011':'johndoe'}
        """
        testcases = dict()
        for key in markup:
            path = key.split('*')[0]
            path = path.rstrip('/')
            for title in self._get_wiki_pages(path):
                testcases[title] = markup[key]
        return testcases

    def _build_testcases_wiki(self, testcases):
        """ builds the testcases in wiki syntax
            returns wikitext
        """
        text = "\n== Zu testende Testcases ==\n||'''Testcase'''||'''User'''||\n"
        for key in testcases:
            text += '||%s||%s||\n' % (key, testcases[key])
        return text

    def _build_configs_wiki(self,config):
        """ builds wiki formatting for the configuration table
        """
        text = "== Testparameter ==\n||'''Attribut'''||'''Wert'''||\n"
        table = ''
        for key in config.keys():
            table += '||%s||%s||\n' % (key, config[key])
        return text + table

class TestCaseMacro(WikiMacroBase):
    """TestCase macro.
       Validates a TestCase wiki page.
       Usage::

           {{{
           #!TestCase
           foo
           bar
           }}}
    """

    revision = "$Rev$"
    url = "$URL$"

    def expand_macro(self, formatter, name, text, args):
        """Execute the macro
        """
        from TestcaseParser import TestcaseParser
        parser = TestcaseParser(self.env)
        out = StringIO.StringIO()
        f = Formatter(self.env, formatter.context)
        try:
            parser.parseTestcase(text=text)
        except Exception, e:
            out.write(system_message("Parsing error", text=e))
        # TODO: Escape wiki markup for text
        #return
        #matt = Formatter(self.env, formatter.context)
        #matt.format(text,out)
        f.format(text, out)
        return Markup(out.getvalue())

    def _format_TestCase(self, env, formatter, case):
        oneliner = Formatter(env, formatter.context)
        out = StringIO.StringIO()
        # format title
        oneliner.format(case.title, out)
        # format description
        oneliner.format(case.desc, out)
        for action in case.actions:
            try:
                oneliner.format(action.title, out)
                oneliner.format(action.description, out)
                oneliner.format(action.expected_result, out)
            except Exception, e:
                #oneliner.system_message(action.title, out)
                #oneliner.system_message(action.description, out)
                #oneliner.system_message(action.expected_result, out)
                print e
        return out

# vim: set ft=python ts=4 sw=4 expandtab :
