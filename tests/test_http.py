from sniper.http import Url
from sniper.tests import TestCase


class TestUrlObject(TestCase):
    def test_replace_query(self):
        url = Url.from_uri(
            '/xxx?aaa=1&bbb=2&ccc=3'
        )
        url.replace_query(aaa=4)
        self.assertEqual(
            '/xxx?aaa=4&bbb=2&ccc=3',
            url.to_uri()
        )

    def test_replace_query_not_exist(self):
        url = Url.from_uri(
            '/xxx?aaa=1&bbb=2&ccc=3'
        )
        url.replace_query(ddd=4)
        self.assertEqual(
            '/xxx?aaa=1&bbb=2&ccc=3&ddd=4',
            url.to_uri()
        )

    def test_replace_query_duplicated_name(self):
        url = Url.from_uri(
            '/xxx?aaa=1&bbb=2&aaa=3'
        )
        url.replace_query(aaa=4)
        self.assertEqual(
            '/xxx?aaa=4&bbb=2&aaa=3',
            url.to_uri()
        )
