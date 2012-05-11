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
#from elixir import *
#import datetime

import trac.db
from trac.db import with_transaction

__author__ = 'Otto Hockel <otto.hockel@inquant.de>'
__docformat__ = 'plaintext'

#metadata.bind = "sqlite:///testmanager.sqlite"
#metadata.bind.echo = True

class TracDBModel(object):
    """ Generic DB Model
    """

    def __init__(self, env):
        self.env = env
        self.db  = env.get_db_cnx()
        self.cursor = self.db.cursor()

    def __repr__(self):
        return "<TestManager:TracDBModel>"

class Testaction(TracDBModel):
    """ Testaction model
        an action is part of a testcase
    """

    #def __init__(self,env):
        #super(Testaction, self).__init__(env)

    #id              
    #testcase        
    #comment         
    #description     
    #status          
    #expected_result 

    def __repr__(self):
        return '<Testaction: "%s">' % (self.title)

class Testcase(TracDBModel):
    """ Testcase model
    """

    #def __init__(self,env):
        #super(Testcase, self).__init__(env)

    #id      
    #wiki    
    #title   
    #tester  
    #actions
    #testrun 

    def __repr__(self):
        return '<Testcase: "%s">' % (self.title)

# vim: set ft=python ts=4 sw=4 expandtab :
