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

# testman specific imports
from interfaces import ITestManagerPanelProvider
from config import MANAGER_PERMISSION, TESTER_PERMISSION

import db_models
import models

class TestManagerPlugin(Component):
    """ TRAC Group Administration Plugin
    """

    panel_providers = ExtensionPoint(ITestManagerPanelProvider)

    implements(INavigationContributor, IRequestHandler, ITemplateProvider)

    def __init__(self):
        Component.__init__(self)
        #db_models.initenv(self.env)

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
            yield 'mainnav', 'TestManager', tag.a(_('TestManager'), href=req.href.TestManager(),
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

class HomePanel(Component):
    """ start page of testmanager, renders the content of wiki page
        TestManagerHome
        this page is displayed by default when clicking the
        testmanager tab (because section *general* comes before the other sections in alphabet)
    """
    implements(ITestManagerPanelProvider)
    def __init__(self):
        Component.__init__(self)
        #db_models.initenv(self.env)

    def get_admin_panels(self, req):
        """ returns the Section and the Name for the Navigation
        """
        yield ('general', _('General'), 'home', _('Home'))


    def render_admin_panel(self, req, cat, page, path_info):
        """ main request handler
        """
        if TESTER_PERMISSION in req.perm:
            data = dict() #template data
            data["info"] = req.args.get("info", "")
            data["warning"] = req.args.get("warning", "")
            data["error"] = req.args.get("error", "")
    
            pagename = "TestManagerHome"
            data["pagename"] = pagename
            data['page'] = wiki_to_html(WikiPage(self.env, pagename).text, self.env, req)
            add_stylesheet(req, 'common/css/wiki.css')
            add_stylesheet(req, 'TestManager/css/testmanager.css')
            data["title"] = 'Testmanager Home'
    
            return 'TestManager_base.html' , data
    
class TestPlanPanel(Component):
    """ Link to available TestPlans
    """
    implements(ITestManagerPanelProvider)
    def __init__(self):
        Component.__init__(self)
        db_models.TRACENV= self.env

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

        if 'start_plan' in req.args:

            # TODO: start testplan in sep. funktion auslagern
            pagename = req.args['start_plan']
            self.log.debug("trying to start testplan " + pagename)
            run = models.TestRun()
            try:
                run.setup(self.env, pagename, req.authname)
            except TracError:
                data['error'] += run.errors

        # render plans
        runs = models.TestRun().query(self.env, status='accepted')
        # TODO: populate with TestRun model
        for run in runs:
            from genshi.builder import tag
            run['ref'] = tag.a('#', run['id'], ' ', run['summary'], href=req.href.ticket(run['id']))
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
        data["defect_runs"] = models.TestRun().query(self.env, status='new')
        data["title"] = 'TestPlans'
        return data['page'] , data

class TestCasesPanel(Component):
    """ Link to available TestPlans
    """
    implements(ITestManagerPanelProvider)
    # XXX: this is not very cool
    def __init__(self):
        Component.__init__(self)

    def get_admin_panels(self, req):
        """ returns the Section and the Name for the Navigation
        """
        yield ('general', _('General'), 'testcases', _('TestCases'))

    def render_admin_panel(self, req, cat, page, path_info):
        """ main request handler
        """
        if TESTER_PERMISSION in req.perm:
            data = dict() #template data
            data["info"] = req.args.get("info", "")
            data["warning"] = req.args.get("warning", "")
            data["error"] = req.args.get("error", "")
            # get all TestCases assigned to the user and have status "not tested"

            tcs = models.TestCaseFilter()
            tc_list = tcs.get(user= req.authname, status= models.NOT_TESTED)
            if not tc_list:
                data["info"] = 'no testcases available'
            else:
                # build link with genshi
                for tc in tc_list:
                    # refer to the testaction module to load the testcase execution
                    # tc.ref = tag.a(tc.wiki, href=req.href.testaction(tc.id))
                    # url = self.env.abs_href("/TestManager/general/testcase/"+tc.id ) 
                    tc.ref = tag.a(tc.wiki, href='#',
                            onclick='window.open("testcase/%s", "Popupfenster", "width=400,height=300,resizable=yes");' % tc.id)
                data["testcases"] = tc_list
            # The template to be rendered
            data["page"] = 'TestManager_base.html'
            data["title"] = 'TestCases'

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
        # should not be visible
        yield ('general', _('General'), 'testcase', _('TestCase'))

    def match_request(self, req):
        match = re.match(r'/testcase/([0-9]+)$', req.path_info)
        if match:
            req.args['id'] = match.group(1)
            return True

    def render_admin_panel(self, req, cat, page, path_info):
        """ main request handler
        """
        if TESTER_PERMISSION in req.perm:
            data = dict() #template data
            data["info"] = req.args.get("info", "")
            data["warning"] = req.args.get("warning", "")
            data["error"] = req.args.get("error", "")
            data["id"] = req.args.get("id", "")
            data["page"] = 'TestManager_accordion.html'
            # TODO: get the testcase
            if data["id"]:
                import models

                testcase = models.TestCaseFilter(id=data['id'])
                if not testcase:
                    # not found
                    data["error"] = 'the requested testcase could not be found or has been erased'
                else:
                    if req.authuser != testcase.tester:
                        # assigned to someone else - but can be done by mr urlaubsvertretung
                        data["warning"] = 'this testcase has been assigned to %s' % testcase.tester
                    # TODO: datenbank auslesen usw usf
                    data["execute"] = testcase
                    data["title"] = 'TestCase %s' % testcase.id
            return data["page"] , data

class TestManagerPermissions(Component):
    """ This class covers the permissions
        @see: config.py
    """
    implements(IPermissionRequestor)
    def get_permission_actions(self):
        return (MANAGER_PERMISSION, TESTER_PERMISSION)

# vim: set ft=python ts=4 sw=4 expandtab :
