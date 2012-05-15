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
import urllib

from genshi.builder import tag
from genshi.util import plaintext

from trac.core import Component
from trac.core import ExtensionPoint
from trac.core import implements

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
from trac.wiki.formatter import format_to_html
from trac.wiki.parser import WikiParser
from trac.mimeview.api import Context
from trac.resource import Resource

from interfaces import ITestManagerPanelProvider

class TestManagerPlugin(Component):
    """ TRAC Group Administration Plugin
    """

    panel_providers = ExtensionPoint(ITestManagerPanelProvider)

    implements(INavigationContributor, IRequestHandler, ITemplateProvider)

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        """ This method is only called for the `IRequestHandler` processing the
        request.

        It should return the name of the navigation item that should be
        highlighted as active/current.
        """
        return 'TestManager'

    def get_navigation_items(self, req):
        """ Should return an iterable object over the list of navigation items
        to add, each being a tuple in the form (category, name, text).
        """
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
        # add default trac admin css
        add_stylesheet(req, 'common/css/admin.css')
        # custom css
        add_stylesheet(req, 'TestManager/stylesheets/TestManager.css')

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
    """ start page of teamchill, renders the content of wiki page
        TeamChillStart
        this page is displayed by default when clicking the 
        teamchill tab (because section *general* comes before the other sections in alphabet)
    """
    implements(ITestManagerPanelProvider)

    def get_admin_panels(self, req):
        """ returns the Section and the Name for the Navigation
        """
        yield ('general', _('General'), 'home', _('Home'))


    def render_admin_panel(self, req, cat, page, path_info):
        """ main request handler
        """
        data = dict() #template data
        data["info"] = req.args.get("info", "")
        data["warning"] = req.args.get("warning", "")
        data["error"] = req.args.get("error", "")

        pagename = "TestManagerHome"
        data["pagename"] = pagename
        data["page"] = WikiPage(self.env, pagename)
        add_stylesheet(req, 'common/css/wiki.css')

        return 'TestManager_base.html' , data
    
class TestPlanPanel(Component):
    """ Link to available TestPlans
    """
    implements(ITestManagerPanelProvider)
    
    def get_admin_panels(self, req):
        """ returns the Section and the Name for the Navigation
        """
        yield ('general', _('General'), 'testplans', _('TestPlans'))


    def render_admin_panel(self, req, cat, page, path_info):
        """ main request handler
        """        
        data = dict() #template data
        data["info"] = req.args.get("info", "")
        data["warning"] = req.args.get("warning", "")
        data["error"] = req.args.get("error", "")
        # The template to be rendered
        data["page"] = 'TestManager_base.html'
        # XXX: this is all gay
        #      available testplans
        testplans = []
        #import pdb; pdb.set_trace()
        from TestManagerLib import *
        ret = getTestRuns()
        for testplan in WikiSystem(self.env).get_pages('Testplan'):
            testplans.append(testplan.title())
        if len(testplans) < 1:
            data["info"] = 'There are no running testplans'
        data["testplans"] = testplans

        return 'TestManager_base.html' , data

class TestCasesPanel(Component):
    """ Link to available TestPlans
    """
    implements(ITestManagerPanelProvider)
    
    def get_admin_panels(self, req):
        """ returns the Section and the Name for the Navigation
        """
        yield ('general', _('General'), 'testcases', _('TestCases'))

    def render_admin_panel(self, req, cat, page, path_info):
        """ main request handler
        """
        data = dict() #template data
        data["info"] = req.args.get("info", "")
        data["warning"] = req.args.get("warning", "")
        data["error"] = req.args.get("error", "")
        data["info"] = 'no testcases available'
        # The template to be rendered
        data["page"] = 'TestManager_base.html'

        return 'TestManager_base.html' , data

class TestManagerPermissions(Component):
    """ This class covers the permissions
    """
    implements(IPermissionRequestor)
    def get_permission_actions(self):
        return ('TM_TESTMANAGER', 'TM_TESTER')

# vim: set ft=python ts=4 sw=4 expandtab :
