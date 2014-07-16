# -*- coding: utf-8 -*-
#
# File: utils.py
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

from testmanconst import *

COLOR = {
    #"green": "#899639",
    #"blue": "#0080BC",
    #"red": "#A90050",
    #"grey": "#4E4E4E",
    #"yellow": "#FFB900"
}

reverse_dict = lambda x: dict(zip(x.values(), x.keys()))

def get_status_color(status):
    colors = {
            PASSED : COLOR.get("green", "#66FF00"),
            PASSED_COMMENT : COLOR.get("yellow", "#FFFF00"),
            FAILED : COLOR.get("red", "#FF0033"),
            SKIPPED : COLOR.get("grey", "#AAAAAA"),
            "default" : "#FFFFFF",
            }
    if status in colors:
        return colors[status]
    else:
        return colors["default"]

def safe_unicode(value, encoding='utf-8'):
    """Converts a value to unicode, even it is already a unicode string.

        copied from Products.CMFPlone.utils

        >>> safe_unicode('spam')
        u'spam'
        >>> safe_unicode(u'spam')
        u'spam'
        >>> safe_unicode(u'spam'.encode('utf-8'))
        u'spam'
        >>> safe_unicode('\xc6\xb5')
        u'\u01b5'
        >>> safe_unicode(u'\xc6\xb5'.encode('iso-8859-1'))
        u'\u01b5'
        >>> safe_unicode('\xc6\xb5', encoding='ascii')
        u'\u01b5'
        >>> safe_unicode(1)
        1
        >>> print safe_unicode(None)
        None
    """
    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        try:
            value = unicode(value, encoding)
        except (UnicodeDecodeError):
            value = value.decode('utf-8', 'replace')
    return value

# vim: set ft=python ts=4 sw=4 expandtab :
