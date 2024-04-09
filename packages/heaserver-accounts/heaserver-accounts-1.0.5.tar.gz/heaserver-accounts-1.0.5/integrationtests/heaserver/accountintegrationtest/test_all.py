from .testcase import AWSAccountTestCase
from heaserver.service.testcase.mixin import GetAllMixin, GetOneMixin


# class TestDeleteAccount(AWSAccountTestCase, DeleteMixin):
#     pass
#
#
class TestGetAccounts(AWSAccountTestCase, GetAllMixin):
    pass


class TestGetAccount(AWSAccountTestCase, GetOneMixin):
    pass
#
#
# class TestPutAccount(AWSAccountTestCase, PutMixin):
#     pass
#
#
# class TestPostAccount(AWSAccountTestCase, PostMixin):
#     pass
