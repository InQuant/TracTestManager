# -*- coding: utf-8 -*-
#
# File: interfaces.py
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

__author__ = 'Hans-Peter Locher <hans-peter.locher@inquant.de>'
__docformat__ = 'plaintext'

from trac.core import Interface


class ITestManagerPanelProvider(Interface):
    """ Extension point interface
    """

    def get_admin_panels(req):
        """ Return a list of available LDAP Admin panels.

        The items returned by this function must be tuples of the form
        `(category, category_label, page, page_label)`.
        If page_label is None, the panel won't show up in the navigation.
        """

    def render_admin_panel(req, category, page, path_info):
        """ Process a request for an LDAP Admin panel.

        This function should return a tuple of the form `(template, data)`,
        where `template` is the name of the template to use and `data` is the
        data to be passed to the template.
        """

# vim: set ft=python ts=4 sw=4 expandtab :
