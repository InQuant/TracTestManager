# -*- coding: utf-8 -*-
#
# File: api.py
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

__author__ = 'Rainer Hihn <rainer.hihn@inquant.de>'
__docformat__ = 'plaintext'

import re
from trac.core import *
from trac.resource import Resource
from tractags.query import *
from trac.perm import IPermissionRequestor, PermissionError
from trac.web.chrome import add_warning
from trac.wiki.model import WikiPage
from trac.util.text import to_unicode
from trac.util.compat import set, groupby
from trac.resource import IResourceManager, get_resource_url, \
    get_resource_description
from genshi import Markup
from genshi.builder import tag as tag_


class InvalidTagRealm(TracError):
    pass


class ITagProvider(Interface):
    def get_taggable_realm():
        """Return the realm this provider supports tags on."""

    def get_tagged_resources(req, tags=None):
        """Return a sequence of resources and *all* their tags.

        :param tags: If provided, return only those resources with the given
                     tags.

        :rtype: Sequence of (resource, tags) tuples.
        """

    def get_resource_tags(req, resource):
        """Get tags for a Resource object."""

    def set_resource_tags(req, resource, tags):
        """Set tags for a resource."""

    def remove_resource_tags(req, resource):
        """Remove all tags from a resource."""


class DefaultTagProvider(Component):
    """An abstract base tag provider that stores tags in the database.

    Use this if you need storage for your tags. Simply set the class variable
    `realm` and optionally `check_permission()`.

    See tractags.wiki.WikiTagProvider for an example.
    """

    implements(ITagProvider)

    abstract = True

    # Resource realm this provider manages tags for. Set this.
    realm = None

    # Public methods
    def check_permission(self, perm, operation):
        """Delegate function for checking permissions.

        Override to implement custom permissions. Defaults to TAGS_VIEW and
        TAGS_MODIFY.
        """
        map = {'view': 'TEST_CLIENT', 'modify': 'TEST_MANAGER'}
        return map[operation] in perm('tag')
