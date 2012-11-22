import pytest
from trac.core import TracError
#from trac_pytest import build_trac_env
from tractestmanager import TestcaseParser
from trac.wiki import WikiPage

TESTCASE = """
= TestCase Tests zum Testplan hinzufügen =

Usecase: UcTestplanCreate
Der Testmanager möchte TestCase(s) zu einem Testplan hinzufügen 
und diese einem oder mehreren Testern zuweisen. 
Die TestCase(s) liegen bereits in einem vordefinierten 
Format vor und sollen referenziert werden.

    Wikiseite erstellen::
      Titel muss mit **Testplan** beginnen

      Eingabemaske zur Eingabe des Inhalts der Wikiseite wird angezeigt.

    Testmanager fügt Macro hinzu und referenziert tests::
      Der Testplan muss mit einem Makro beginnen, das wie folgt aussieht
      {{{
      {{{
      #!TestPlan
      Id: Testman
      Release: 0.1
      Usecases: UcTestRunEvaluate, UcTestRunInfo, UcTestRunReview, UcTestcaseCreate, UcTestcaseExecute, UcTestplanCreate, UcTestplanStart

      TestCase/TestcaseCreate testadmin
      TestCase/TestplanCreate testadmin
      }}}
      }}}

      Ansicht des Makros

    Testmanager referenziert Tests::
      innerhalb des Macros über die Angabe eines Pfades oder einer ID
      in diesem Beispiel 
      TestCase/TestcaseCreate und
      TestCase/TestplanCreate

      Ansicht des Makros

    Testmanager wählt Tester aus::
      über die Angabe einer Userid innerhalb des Macros
      in diesem Beispiel
      testadmin

      Ansicht des Makros

    Testmanager bestätigt die Änderung der Wikipage::
      durch Klick auf **Submit Changes**

      das Macro wird ausgeführt und listet die hinzugefügten Testcases in Wikinotation.
"""

def test_parseTestcase_NotExistingWikiPage(build_trac_env):
    env = build_trac_env
    tcp = TestcaseParser(env)
    with pytest.raises(TracError):
        # a Wiki Page that doenst exist
        tcp.parseTestcase('NotExistingWikiPage')

def test_parseTestcase_parseWikiPage(build_trac_env):
    env = build_trac_env

    wikipage = WikiPage(env, 'TcTestplanCreate')
    wikipage.text = TESTCASE.decode('utf-8')
    wikipage.save("pytest", "comment", "127.0.0.1")

    tcp = TestcaseParser(env)
    testcase = tcp.parseTestcase(pagename='TcTestplanCreate')
    assert len(testcase.actions) == 5
