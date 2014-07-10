# -*- coding: utf-8 -*-
#
# File: TestManager.py
#
# Copyright (c) InQuant GmbH
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

__author__ = 'Rainer Hihn <rainer.hihn@inquant.de>'
__docformat__ = 'plaintext'

import re
from genshi.builder import tag
from trac.core import Component
from trac.core import ExtensionPoint
from trac.core import implements
from trac.core import TracError

from trac.web import HTTPNotFound
from trac.web import IRequestHandler
from trac.web.api import IRequestFilter
from trac.web.chrome import INavigationContributor
from trac.web.chrome import ITemplateProvider
from trac.web.chrome import add_stylesheet
from trac.web.chrome import add_script

from trac.util.translation import _
from trac.util.compat import partial

from trac.perm import IPermissionRequestor
from trac.perm import PermissionError

from trac.wiki.api import WikiSystem
from trac.wiki import WikiPage
from trac.wiki.formatter import wiki_to_html
from trac.wiki.formatter import format_to_html
from trac.mimeview.api import Context
from trac.resource import Resource
from trac.ticket.api import TicketSystem
from trac.ticket import Ticket
from trac.ticket import Priority

# testman specific imports
from interfaces import ITestManagerPanelProvider
from config import MANAGER_PERMISSION, TESTER_PERMISSION, get_display_states
from tractestmanager.utils import safe_unicode, get_status_color
import tractestmanager.models as models

class TestManagerPlugin(Component):
    """ TRAC Group Administration Plugin
    """

    panel_providers = ExtensionPoint(ITestManagerPanelProvider)

    implements(INavigationContributor, IRequestHandler, ITemplateProvider)

    def __init__(self):
        Component.__init__(self)

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        """ This method is only called for the `IRequestHandler` processing the
        request.

        It should return the name of the navigation item that should be
        highlighted as active/current.
        """
        if TESTER_PERMISSION in req.perm:
            return 'TestManager'

    def get_navigation_items(self, req):
        """ Should return an iterable object over the list of navigation items
        to add, each being a tuple in the form (category, name, text).
        """
        if TESTER_PERMISSION in req.perm:
            yield 'mainnav', 'TestManager', tag.a(_('TestManager'),
                    href=req.href.TestManager(),
                    title=_('TestManager'))
    # IRequestHandler methods
    def match_request(self, req):
        match = re.match('/TestManager(?:/([^/]+))?(?:/([^/]+))?(?:/(.*)$)?',
                         req.path_info)
        if match:
            req.args['cat_id'] = match.group(1)
            req.args['panel_id'] = match.group(2)
            req.args['path_info'] = match.group(3)
            return True

    def process_request(self, req):
        """ process the request and render the response template
        """
        if TESTER_PERMISSION in req.perm:
            # add default trac admin css
            add_stylesheet(req, 'common/css/admin.css')
            # custom css
            add_stylesheet(req, 'TestManager/css/testmanager.css')

            # get the panels and their providers
            panels, providers = self._get_panels(req)
            if not panels:
                # no providers found
                raise HTTPNotFound(_('No TestManager panels available'))

            # Navigation tree
            cat_id    = req.args.get('cat_id') or panels[0][0]
            panel_id  = req.args.get('panel_id')
            path_info = req.args.get('path_info')
            # TODO: what to do? REFACTOR!
            if not panel_id:
                panel_id = filter(lambda panel: panel[0] == cat_id, panels)[0][2]

            provider = providers.get((cat_id, panel_id), None)
            if not provider:
                raise HTTPNotFound(_('Unknown TestManager panel'))

            data = dict()
            if hasattr(provider, 'render_admin_panel'):
                template, data = provider.render_admin_panel(req, cat_id, panel_id, path_info)

            data.update({
                'active_cat': cat_id,
                'active_panel': panel_id,
                'panel_href': partial(req.href, 'TestManager', cat_id, panel_id),
                'panels': [{
                    'category': {'id': panel[0], 'label': panel[1]},
                    'panel': {'id': panel[2], 'label': panel[3]}
                } for panel in panels]
            })

            return template, data, None

    # ITemplateProvider methods
    def get_templates_dirs(self):
        """ Return a list of directories containing the provided template
        files.
        """

        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        """ Return a list of directories with static resources (such as style
        sheets, images, etc.)

        Each item in the list must be a `(prefix, abspath)` tuple. The
        `prefix` part defines the path in the URL that requests to these
        resources are prefixed with.

        The `abspath` is the absolute path to the directory containing the
        resources on the local file system.
        """

        from pkg_resources import resource_filename
        return [("TestManager", resource_filename(__name__, 'htdocs'))]

    # Internal methods
    def _get_panels(self, req):
        """ Return a list of available LDAP Group panels.

        panels = [('general', 'General', 'basics', 'Basic Settings')]
        providers = {('general', 'basics'): <groupadministration.groupadministration.AddLDAPGroupPanel object at ...}
        """
        panels = []
        providers = {}

        for provider in self.panel_providers:
            p = list(provider.get_admin_panels(req))
            for panel in p:
                providers[(panel[0], panel[2])] = provider
                #only show panel if it has a label
                if panel[3]:
                    panels += p

        return panels, providers

class TestPlanPanel(Component):
    """ Link to available TestPlans
    """
    implements(ITestManagerPanelProvider)
    def __init__(self):
        Component.__init__(self)

    def get_admin_panels(self, req):
        """ returns the Section and the Name for the Navigation
        """
        if MANAGER_PERMISSION in req.perm:
            yield ('general', _('General'), 'testplans', _('TestPlans'))


    def render_admin_panel(self, req, cat, page, path_info):
        """ main request handler
        """
        if not MANAGER_PERMISSION in req.perm:
            return

        data = dict() #template data
        data["info"] = req.args.get("info", "")
        data["warning"] = req.args.get("warning", "")
        data["error"] = req.args.get("error", "")
        # The template to be rendered
        data["page"] = 'TestManager_base.html'
        data["testplanlink"] = req.base_url + req.path_info

        if 'start_plan' in req.args:
            # setup and start a new testrun
            pagename = req.args['start_plan']
            self.log.debug("trying to start testplan " + pagename)
            testrun = models.TestRun(self.env)
            try:
                testrun.setup(pagename, req.authname)
                testrun.start()
            except TracError, e:
                data["error"] = safe_unicode(e.message)

        elif 'testplan_to_restart' in req.args:
            # we have a defect testrun to be restarted
            runids = req.args['testplan_to_restart']
            def ensure_list(var):
                if type(var) == list:
                    return var
                else:
                    return [var]
            for runid in ensure_list(runids):
                try:
                    self.log.debug("trying to restart testplan " + runid)
                    testrun = models.TestRun(self.env, runid)
                    testrun.start()
                except TracError, e:
                    data["error"] = safe_unicode(e.message)

        # query and render accepted testruns
        runs = models.TestRunQuery(self.env, status='accepted').execute()

        # TODO: populate with TestRun model
        for run in runs:
            # from genshi.builder import tag
            #run['ref'] = tag.a('#', run['id'], ' ', run['summary'], href=req.href.ticket(run['id']))
            run['ref'] = tag.a('#', run.id, ' ', run.summary, href=req.href.ticket(run.id))

        testplans = list()
        for testplan in WikiSystem(self.env).get_pages('Testplan'):
            testplans.append(testplan)
        if len(testplans) < 1:
            data["info"] = 'There are no testplans'
        if len(runs) < 1:
            data["info"] = 'There are no running testplans'

        # get active and valid testruns
        data["testruns"] = runs
        data["testplans"] = testplans
        # TODO: to be implemented in order to populate an already startet but brick testrun
        data["defect_runs"] = models.TestRunQuery(self.env, status='new').execute()
        for defect_run in data["defect_runs"]:
            defect_run['ref'] = tag.a('#', defect_run.id, ' ',
                    defect_run.summary, href=req.href.ticket(defect_run.id))
        data["title"] = 'TestPlans'
        return data['page'] , data

def build_testcase_link(tm_href, tc):
    # build link with genshi
    url = "%s/testcase/%s" % (tm_href, tc.tcid)
    return tag.a(tc.title.strip('= '), href="#",
        onclick='window.open("%s", "Popupfenster",'\
        '"width=400,height=400,resizable=yes,scrollbars=yes");' % url)

class TestQueryPanel(Component):
    """ Queries testcases via url handler
    """
    implements(ITestManagerPanelProvider)

    def __init__(self):
        Component.__init__(self)

    def get_admin_panels(self, req):
        """ returns the Section and the Name for the Navigation
        """
        yield ( 'general', _('General'), 'testquery', _("TestCases") )

    def render_admin_panel(self, req, cat, page, path_info):
        """ main request handler
        """
        if not TESTER_PERMISSION in req.perm:
            return

        data = dict() #template data
        data["info"] = req.args.get("info", "")
        data["warning"] = req.args.get("warning", "")
        data["error"] = req.args.get("error", "")
        display = get_display_states(self)
        tm_href = self.env.abs_href("TestManager/general")
        # get the testcase filter args
        filters= dict()
        for arg in req.args:
            if arg in models.TC_KEYS:
                filters[arg]= req.args.get(arg, "")

        if filters.get('status'):
            for k,v in display.items():
                if v == filters.get('status'):
                    filters['status'] = k
        runs= list()
        if filters.get('tester') == 'all':
            filters.pop('tester')
        if filters.get('testrun', None) is None:
            runs = models.TestRunQuery(self.env, status='accepted').execute()
        else:
            try:
                runs.append(models.TestRun(self.env,
                    int(filters.get('testrun', None))))
            except TypeError:
                # we have more than one testrun
                for run in filters.get('testrun'):
                    runs.append(models.TestRun(self.env, int(run)))
            finally:
                # drop testrun filter
                filters.pop('testrun')

        for run in runs:
            run.testcases = models.TestCaseQuery(self.env, testrun=run.id, **filters).execute()

            # build link with genshi
            for tc in run.testcases: tc.ref= build_testcase_link(tm_href, tc)

        # The template to be rendered
        display[req.authname] = req.authname
        display['all'] = 'all'
        data["filter"]= {}
        data["testcases"]= runs
        data["page"] = 'TestManager_base.html'
        data["title"] = 'TestCases'

        data["url"] = req.abs_href + req.path_info + "?" + req.query_string
        data["filter_caption"] = {
        'tester': "Tester: ",
            'status' : "Testcase Status: "
        }
        data["filter"] = {
                'tester' : [req.authname, 'all'],
            'status' : [models.FAILED, models.NOT_TESTED, models.SKIPPED, models.PASSED, models.PASSED_COMMENT],
        }
        data['display_filter'] = display
        return 'TestManager_base.html' , data

class TestCasePanel(Component):
    """ a panel to fit requests for executing testcases
    """
    implements(ITestManagerPanelProvider)
    def __init__(self):
        Component.__init__(self)
    def get_admin_panels(self, req):
        """ returns the Section and the Name for the Navigation
        """
        yield ('general', _('General'), 'testcase', _(None))

    def match_request(self, req):
        match = re.match(r'/testcase/([0-9]+)$', req.path_info)
        if match:
            req.args['id'] = match.group(1)
            return True

    def get_default_priority(self):
        return TicketSystem(self.env).default_priority

    def get_priorities(self):
        return [prio.name for prio in Priority.select(self.env)]

    def render_admin_panel(self, req, cat, page, path_info):
        """ main request handler
        """
        display = get_display_states(self)
        if TESTER_PERMISSION in req.perm:
            data = dict() #template data
            data["info"] = req.args.get("info", "")
            data["warning"] = req.args.get("warning", "")
            data["error"] = req.args.get("error", "")
            data["display_status"] = get_display_states(self)
            data["status"] = {display[models.PASSED] : models.PASSED,
                    display[models.FAILED] : models.FAILED,
                    display[models.PASSED_COMMENT] : models.PASSED_COMMENT,
                    display[models.NOT_TESTED] : models.NOT_TESTED,
                    display[models.SKIPPED] : models.SKIPPED}
            data["id"] = req.args.get("path_info", None)
            data["page"] = 'TestManager_accordion.html'
            ############################################################################
            data["url"] = req.abs_href + req.path_info
            # get the testcase

            data['priorities'] = self.get_priorities()
            data['default_priority'] = self.get_default_priority()
            if data["id"]:
                try:
                    testcase = models.TestCaseQuery(self.env,
                            tcid=data['id']).execute()[0]
                    for action in testcase.actions:
                        action.color = {"style" : ("background:%s" % get_status_color(action.status))}
                    data["TestCaseTitle"] = testcase.title.strip('=')
                    data["TestCaseDescription"] = testcase.description
                    data["TestCaseActions"] = testcase.actions
                    data["revision"] = testcase.revision
                    data["title"] = '(%s) ' % testcase.tcid + testcase.wiki
                    # XXX: we have to fix this in 1.0 because wiki_to_html is deprecated
                    for action in testcase.actions:
                        action.description= wiki_to_html(action.description, self.env, req)
                        action.expected_result= wiki_to_html("''Result:''[[BR]]" + action.expected_result, self.env, req)
                        for comment in action.comments:
                            comment["text"] = wiki_to_html(comment["text"], self.env, req)
                    if req.authname != testcase.tester:
                        # assigned to someone else - but can be done by mr urlaubsvertretung
                        data["warning"] = 'this testcase has been assigned to %s' % testcase.tester
                except:
                    # not found
                    data["error"] = 'the requested testcase could not be found or has been erased'
            return data["page"] , data

class TestManagerPermissions(Component):
    """ This class covers the permissions
        @see: config.py
    """
    implements(IPermissionRequestor)
    def get_permission_actions(self):
        return (MANAGER_PERMISSION, TESTER_PERMISSION)


class TestManagerAttachmentScript(Component):
    """ This class adds a javascript to prefill the description of an attachment
    """
    implements(IRequestFilter)

    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        if req.method == 'POST' and req.args.get('testman_cnum', None):
            t = Ticket(self.env, tkt_id=req.args.get('path'))
            cdate = t.get_change(cnum=req.args.get('testman_cnum'))['date']
            comment = t.get_change(cnum=req.args.get('testman_cnum'))['fields']['comment']['new']
            new_comment = u"%s\n attachment added: [attachment:ticket:%s:%s]" % (comment, req.args.get("id"), req.args.get('attachment').filename)
            t.modify_comment(cdate, req.authname, new_comment, when=cdate)
        return handler

    def post_process_request(self, req, template, data, content_type):
        if template == 'attachment.html':
            add_script(req, 'TestManager/js/prefill_att_desc.js')
            if not req.args.get('testman_cnum', None):
                return template, data, content_type
        return template, data, content_type

# vim: set ft=python ts=4 sw=4 expandtab :
