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
from trac.ticket.query import Query as TicketQuery
from trac.ticket.model import Ticket

def _get_wiki_pages(self,prefix):
    """ wrap the wiki api
    """
    for page in WikiSystem(self.env).get_pages(prefix):
        yield page

def add_testrun(env, config, user, macro_text):
    """ add new testrun ticket
    """
    data = dict()
    data['owner'] = user
    data['reporter'] = user
    data['summary'] = config['id']
    data['description'] = macro_text
    data['type'] = 'testrun'
    data['status'] = 'accepted'
    t = Ticket(env)
    t.populate(data)
    return t.insert()

def defect_testrun(env, id, error_message):
    t = Ticket(env, id)
    t['status'] = 'new'
    t['description'] += error_message
    return t.save_changes()

# vim: set ft=python ts=4 sw=4 expandtab :
