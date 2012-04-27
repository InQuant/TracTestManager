from trac.core import Component, implements
from trac.perm import IPermissionRequestor
class MyPermissions(Component):
    implements(IPermissionRequestor)
    def get_permission_actions(self):
        return ('TEST_MANAGER', 'TEST_CLIENT')
