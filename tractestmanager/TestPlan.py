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

__author__ = 'Otto Hockel <otto.hockel@inquant.de>'
__docformat__ = 'plaintext'

from genshi.core import Markup

from trac.wiki.macros import WikiMacroBase
from trac.wiki import Formatter
import StringIO

class TestPlanMacro(WikiMacroBase):
    """Testplan macro.

    Note that the name of the class is meaningful:
     - it must end with "Macro"
     - what comes before "Macro" ends up being the macro name

    The documentation of the class (i.e. what you're reading)
    will become the documentation of the macro, as shown by
    the !MacroList macro (usually used in the WikiMacros page).
    """

    revision = "$Rev$"
    url = "$URL$"

    def expand_macro(self, formatter, name, text, args):
        """Execute the testplan-macro::
            
            {{{
            #!TestPlan
            Id: TA14
            Testart: UsecaseTest 
            Build: DC-3.1.1
            Konfiguration: IE7-Win, FF-LUX
            Usecases: BaugruppenVerwalten, ObjekteSuchen

            Testcases/SaveAsEinerBaugruppe lmende
            Testcases/ErzeugenEinerBaugruppe lmende
            Testcases/Suchen/* mmuster
            }}}

        """
        conf = self.parse_config(text)
        markupreturn = 'TestPlan, text = %s, args = %s' % \
            (Markup.escape(text), Markup.escape(repr(args)))
        wikisite = '== Executing wiki macros =='
        out = StringIO.StringIO()
        Formatter(self.env, formatter.context).format(wikisite,out)
        return Markup(out.getvalue())

    def parse_config(self,text):
        lines = text.splitlines()
        config = []
        for line in lines:
            if ':' in line:
                config.append(line)
        return self._parse_attributes(config)

    def get_wiki_page(self,path):
        # put some information about a wiki page that has been selected
        print "getting wiki page for \"" + path + "\"..."
        pass

    def _parse_attributes(self,attribute_lines):
        attributes = dict()
        for line in attribute_lines:
            line.replace(' ','')
            x,y = line.split(':')
            attributes[x] = y
        return attributes

# vim: set ft=python ts=4 sw=4 expandtab :
