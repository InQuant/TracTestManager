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

from trac.wiki import WikiSystem
from models import PASSED, PASSED_COMMENT, FAILED, SKIPPED

def _get_wiki_pages(self,prefix):
    """ wrap the wiki api
    """
    for page in WikiSystem(self.env).get_pages(prefix):
        yield page

def get_status_color(status):
    colors = {
            PASSED : "#66FF00",
            PASSED_COMMENT : "#FFFF00",
            FAILED : "#FF0033",
            SKIPPED : "#AAAAAA",
            "default" : "#FFFFFF",
            }
    if status in colors:
        return colors[status]
    else:
        return colors["default"]

# vim: set ft=python ts=4 sw=4 expandtab :
