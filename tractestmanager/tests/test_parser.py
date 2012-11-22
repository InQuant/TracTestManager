import pytest
from trac.core import TracError
#from trac_pytest import build_trac_env
from tractestmanager import TestcaseParser
from trac.wiki import WikiPage

def test_parseTestcase_NotExistingWikiPage(build_trac_env):
    env = build_trac_env
    tcp = TestcaseParser(env)
    with pytest.raises(TracError):
        # a Wiki Page that doenst exist
        tcp.parseTestcase('NotExistingWikiPage')

def test_parseTestcase_parseWikiPage(build_trac_env):
    env = build_trac_env

    f = open("src/TracTestManager/docs/wiki/TcTestplanCreate")

    wikipage = WikiPage(env, 'TcTestplanCreate')
    wikipage.text = f.read().decode('utf-8')
    wikipage.save("pytest", "comment", "127.0.0.1")

    tcp = TestcaseParser(env)
    tcp.parseTestcase(pagename='TcTestplanCreate')

    assert 1
