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
from elixir import *
import datetime

__author__ = 'Otto Hockel <otto.hockel@inquant.de>'
__docformat__ = 'plaintext'

metadata.bind = "sqlite:///testmanager.sqlite"
metadata.bind.echo = True

class Testaction(Entity):
    """ Testaction model
        an action is part of a testcase
    """
    
    id       = Field(Integer, primary_key=True)
    title    = Field(UnicodeText)
    desc     = Field(UnicodeText)
    result   = Field(UnicodeText)
    testcase = ManyToOne('Testcase')

    def __repr__(self):
        return '<Testaction: "%s">' % (self.title)

class Testcase(Entity):
    """ Testcase model
    """

    id        = Field(Integer, primary_key=True)
    wiki      = Field(Unicode(128))
    title     = Field(UnicodeText)
    tester    = Field(Unicode(128))
    actions   = OneToMany('Testaction')
    testcases = ManyToOne('Testrun')

    def __repr__(self):
        return '<Testcase: "%s">' % (self.title)

class Testrun(Entity):
    """ Testrun model
        a Testplan is expected to be a wiki page
    """

    id				= Field(Integer, primary_key=True)
    start			= Field(DateTime, default=datetime.datetime.now)
    end				= Field(DateTime)
    config		= Field(UnicodeText)
    testcases = OneToMany('Testcase')

    def __repr__(self):
        return '<Testrun: started on "%s">' % (self.start)

