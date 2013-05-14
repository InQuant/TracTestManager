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
from genshi.builder import tag

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
from trac.web.chrome import Chrome, ITemplateProvider, add_stylesheet, add_script
from trac.wiki.api import IWikiMacroProvider, parse_args

import StringIO
import string

from TestManagerLib import safe_unicode
from TestcaseParser import TestcaseParser, TestPlanMacroParser

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
           ErzeugenEinerBaugruppe lmende, mmuster
           Suchen/* mmuster
           }}}
    """

    revision = "$Rev$"
    url = "$URL$"

    def expand_macro(self, formatter, name, text, args):
        """Execute the macro
        """
        self.env.log.debug("TestPlanMacro.expand_macro()")

        parser = TestcaseParser(self.env)

        self.env.log.debug( "name: %s", str(name))
        self.env.log.debug( "args: %s", str(args))
        self.env.log.debug( "text: %s", str(text))

        errors = list()
        # Parse config and testcases
        attrs, tcnames_and_users = TestPlanMacroParser(self.env).parse_config(text)
        self.log.debug("attrs: %s" % attrs)

        # syntax check the testcases
        for tcname, users in tcnames_and_users:
            try:
                parser.parseTestcase(tcname)
            except TracError, e:
                # FIXME: commented because auf genshi unicode error - raised
                # instead, see other FIXME below!
                #"""
                error_message = safe_unicode("Parsing error in Testcase %s:" %
                        tcname)
                errors.append(system_message(error_message,
                    text= safe_unicode(e.message)))
                #"""
                #raise TracError(safe_unicode("Parsing error in Testcase %s: %s" %
                        #(tcname, e.message)))


        # Build config params in wiki syntax
        text = self._build_configs_wiki(attrs)
        self.log.debug(text)

        # Build testcase section in wiki syntax as a table
        testcases = self._build_testcases_wiki(tcnames_and_users)
        text += testcases
        out = StringIO.StringIO()

        # TODO: Escape wiki markup for text
        Formatter(self.env, formatter.context).format(safe_unicode(text),out)

        # FIXME: commented because auf genshi unicode error - see raise above
        for e in errors:
            out.write(e)

        return Markup(out.getvalue())

    def _build_testcases_wiki(self, tcnames_and_users):
        """ builds the testcases names and users in wiki syntax
            returns wikitext
        """
        self.log.debug( "TestPlanMacro._build_testcases_wiki(%s)" % tcnames_and_users)
        text = u"\n== Zu testende Testcases ==\n||'''Testcase'''||'''User'''||\n"
        for tcname, users in tcnames_and_users:
            text += '||[wiki:%s]||%s||\n' % (tcname, ",".join(users))
        return safe_unicode(text)

    def _build_configs_wiki(self, config):
        """ builds wiki formatting for the configuration table
        """
        text = u"== Testparameter ==\n||'''Attribut'''||'''Wert'''||\n"
        table = u''
        for key in config.keys():
            table += u'||%s||%s||\n' % (unicode(key), unicode(config[key]))
        return safe_unicode(text + table)

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
        #args = {'group': 'status' }
        args = { }
        args.update(constraints)
        args.update(extra_args)
        return req.href("TestManager/general/testquery", args)
    return {'stats': stat,
            'stats_href': query_href(stat.qry_args),
            'interval_hrefs': [query_href(interval['qry_args'])
                            for interval in stat.intervals]}

class TestEvalMacro(WikiMacroBase):
    """Test query wiki macro plugin for Trac Testman, evaluates the status of
    testcases not testactions!

    usage: TestEval(<kwargs>), e.g.: {{{[[TestEval(testrun=18|19,
    tester=testadmin)]]}}}

    """
    implements(ITemplateProvider)

    # TODO: we got all args in common with TestRunMonitorMacro
    def _parse_macro_content(self, content, req):
        args, kwargs = parse_args(content, strict=False)
        ids = list()
        if '|' in kwargs['testrun']:
            for i in kwargs['testrun'].split("|"):
                ids.append(i)
            kwargs['testrun'] = ids
        assert not args and not ('status' in kwargs or 'format' in kwargs), \
          "Invalid input!"

        return kwargs

    def expand_macro(self, formatter, name, content):
        #import ipdb; ipdb.set_trace();
        req = formatter.req
        kwargs = self._parse_macro_content(content, req)
        self.env.log.debug("Macro Args: %s" % kwargs)

        # merge tcs with the same name
        try:
            merge = kwargs.pop("merge")
        except KeyError:
            merge = False

        # Create & execute the query string
        from models import TestCaseQuery, STATUSES
        tcs= TestCaseQuery( self.env, **kwargs ).execute()
        if not merge:
            tcs= TestCaseQuery( self.env, **kwargs ).execute()
        else:
            #tcs = TestCaseQuery(self.env, testrun=kwargs['testrun']).execute()
            tcs= TestCaseQuery( self.env, **kwargs ).execute()
            merged = dict()
            for tc in tcs:
                if merged.get(tc.wiki, None):
                    # if we have a double, the worst status wins
                    if not STATUSES.index(merged[tc.wiki].status) > STATUSES.index(tc.status):
                        merged[tc.wiki] = tc
                else:
                    merged[tc.wiki] = tc
            # now we generate the list :)
            tcs = merged.values()

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

class TestRunMonitorMacro(WikiMacroBase):
    """Test query macro for Testruns to display the overall-status

    usage: e.g.: [[TestRunMonitor(testrun= 18)]]

    """

    # TODO: we got all args in common with TestEvalMacro
    def _parse_macro_content(self, content, req):
        args, kwargs = parse_args(content, strict=False)
        if '|' in kwargs['testrun']:
            ids = list()
            for i in kwargs['testrun'].split("|"):
                ids.append(i)
            kwargs['testrun'] = ids
        assert not args and not ('status' in kwargs or 'format' in kwargs), \
          "Invalid input!"

        return kwargs

    def expand_macro(self, formatter, name, content):
        req = formatter.req
        kwargs = self._parse_macro_content(content, req)
        self.env.log.debug("Macro Args: %s" % kwargs)
        out = StringIO.StringIO()

        self.components = self.compmgr.components
        # get testrun
        from models import TestCaseQuery
        # TODO: get the config - we have to make the config persistent in some way
        # now we take more than one testrun to monitor
        # TODO: should we really split this here?
        tcs = TestCaseQuery(self.env, testrun=kwargs['testrun']).execute()
        text = "\n||'''Testcase'''||'''User'''||'''Status'''||\n"
        from TestManagerLib import get_status_color
        for tc in tcs:
            tc.color = get_status_color(tc.status)
            tc_data = {
                    "testcase" : "[%s/TestManager/general/testcase/%s #%s %s]" %
                    (req.abs_href(), tc.id, tc.id, tc.wiki),
                    "tester" : tc.tester,
                    "status" : tc.status,
                    "color" : tc.color
                    }
            text += """{{{#!td style="background: %(color)s"
              %(testcase)s
            }}}
            {{{#!td style="background: %(color)s"
              %(tester)s
            }}}
            {{{#!td style="background: %(color)s"
              %(status)s
            }}}
            |----------------
            """ % tc_data
        # ... and finally display them
        Formatter(self.env, formatter.context).format(text,out)
        return Markup(out.getvalue())


class ProjectEvalMacro(WikiMacroBase):
    """project evaluation macro.

       Usage::
           {{{
           #!ProjectEval
           Project: Manage Tests
           TestRuns: 28, 29, 30, 31
           Build: TM-3.1.1

           Manage Tests: BucTestPrepare, BucTestExecute

           BucTestPrepare: UcTestcaseCreate, UcTestplanCreate, UcTestplanStart
           BucTestExecute: UcTestcaseExecute, UcTestRunInfo, UcTestRunReview, UcTestRunEvaluate

           UcTestplanStart: TcTestplanStart, TcTestplanStartFailed
           UcTestplanCreate: TcTestplanCreate
           UcTestcaseCreate: TcTestcaseCreate
           UcTestcaseExecute: TcTestCaseExecute*
           UcTestRunReview: TcTestRunReview*
           UcTestRunInfo: TcTestRunInfo
           UcTestRunEvaluate: TcTestRunEvaluate, TcTestRunEvaluateProjectEval
           }}}
    """
    revision = "$Rev$"
    url = "$URL$"

    def expand_macro(self, formatter, name, text, args):
        """Execute the macro
        """
        req = formatter.req
        add_stylesheet(req, "TestManager/css/jquery.jOrgChart.css")
        add_script(req, "TestManager/js/jquery.jOrgChart.js")
        add_script(req, "TestManager/js/start_org.js")

        from models import Element
        con = self._parse_macro_content(text, req)
        out = StringIO.StringIO()
        con.to_list()
        text = """{{{#!html
        <ul id='org' style='display:none'>
        %s</ul>
        <div id="chart" class="orgChart"></div>
        }}}""" % con.to_list()
        Formatter(self.env, formatter.context).format(safe_unicode(text),out)
        return Markup(out.getvalue())

    def _parse_macro_content(self, content, req):
        data = dict()
        for line in content.split('\n'):
            if line:
                key, val = line.split(':')
                data[key] = val.strip()
        return self._build_project(data)

    def _build_project(self, data):
        if not 'Project' in data.keys():
            return None
        else:
            from models import Element
            def structure_from_dict(data, root):
                elements = list()
                vals = data.get(root.value, None)
                if not vals:
                    # no children, break
                    return list()
                for c in vals.split(', '):
                    el = Element(c)
                    nodes = structure_from_dict(data, el)
                    if nodes:
                        el.set_children(nodes)
                    elements.append(el)
                return elements

            root = Element(data['Project'])
            root.set_children(structure_from_dict(data, root))
        return root


# vim: set ft=python ts=4 sw=4 expandtab :
