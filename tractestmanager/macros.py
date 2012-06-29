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

from trac.config import ExtensionOption
from trac.ticket.query import Query
from trac.ticket.roadmap import ITicketGroupStatsProvider, \
                                apply_ticket_permissions, get_ticket_stats
from trac.core import *
from trac.web.chrome import Chrome, ITemplateProvider, add_stylesheet
from trac.wiki.api import IWikiMacroProvider, parse_args

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

def my_query_stats_data( req, stat, constraints ):
    def query_href(extra_args):
        args = {'group': 'status' }
        args.update(constraints)
        args.update(extra_args)
        return req.href.query(args)
    return {'stats': stat,
            'stats_href': query_href(stat.qry_args),
            'interval_hrefs': [query_href(interval['qry_args'])
                            for interval in stat.intervals]}

class TestEvalMacro(WikiMacroBase):
    """Test query wiki macro plugin for Trac Testman, evaluates the status of
    testcases not testactions!

    usage: TestEval(<kwargs>), e.g.: [[TestEval(testrun= 18, tester= testadmin)]]

    """
    implements(ITemplateProvider)

    def _parse_macro_content(self, content, req):
        args, kwargs = parse_args(content, strict=False)
        assert not args and not ('status' in kwargs or 'format' in kwargs), \
          "Invalid input!"

        return kwargs

    def expand_macro(self, formatter, name, content):
        req = formatter.req
        kwargs = self._parse_macro_content(content, req)
        self.env.log.debug("Macro Args: %s" % kwargs)

        # Create & execute the query string
        from models import TestCaseQuery
        tcs= TestCaseQuery( self.env, **kwargs ).execute()

        # Calculate stats
        from evaluate import TestCaseStatus
        stats = TestCaseStatus(self.env).get_testcase_stats( tcs )
        stats_data = my_query_stats_data(req, stats, kwargs)

        self.components = self.compmgr.components
        # ... and finally display them
        add_stylesheet(req, 'common/css/roadmap.css')
        add_stylesheet(req, 'TestManager/css/testmanager.css')
        chrome = Chrome(self)
        return chrome.render_template(req, 'progressmeter.html', stats_data,
                                      fragment=True)

    ## ITemplateProvider methods
    def get_htdocs_dirs(self):
        return []

    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]

# vim: set ft=python ts=4 sw=4 expandtab :
