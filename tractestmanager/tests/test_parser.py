import pytest
from trac.core import TracError
from trac_pytest import build_trac_env
from tractestmanager import TestcaseParser

def test_parseTestcase_NotExistingWikiPage(build_trac_env):
    env = build_trac_env
    tcp = TestcaseParser(env)
    with pytest.raises(TracError):
        # a Wiki Page that doenst exist
        tcp.parseTestcase('NotExistingWikiPage')

