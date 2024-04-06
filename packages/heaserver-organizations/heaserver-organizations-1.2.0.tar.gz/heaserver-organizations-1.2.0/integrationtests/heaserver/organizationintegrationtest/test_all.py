from .testcase import TestCase
from heaserver.service.testcase.mixin import GetOneMixin, GetAllMixin, PostMixin, PutMixin, DeleteMixin


class TestGet(TestCase, GetOneMixin):
    pass

class TestGetAll(TestCase, GetAllMixin):
    pass


class TestPost(TestCase, PostMixin):
    pass


class TestPut(TestCase, PutMixin):
    pass


class TestDelete(TestCase, DeleteMixin):
    pass
