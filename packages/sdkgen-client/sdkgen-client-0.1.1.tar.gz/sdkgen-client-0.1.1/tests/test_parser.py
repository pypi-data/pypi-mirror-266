import datetime
import unittest

from src.sdkgen import Parser
from tests.generated.test_object import TestObject


class TestParser(unittest.TestCase):
    def test_url(self):
        parser = Parser("https://api.acme.com/")

        self.assertEqual(parser.url("/foo/bar", {}), "https://api.acme.com/foo/bar")
        self.assertEqual(parser.url("/foo/:bar", {"bar": "foo"}), "https://api.acme.com/foo/foo")
        self.assertEqual(parser.url("/foo/$bar<[0-9]+>", {"bar": "foo"}), "https://api.acme.com/foo/foo")
        self.assertEqual(parser.url("/foo/$bar", {"bar": "foo"}), "https://api.acme.com/foo/foo")
        self.assertEqual(parser.url("/foo/{bar}", {"bar": "foo"}), "https://api.acme.com/foo/foo")
        self.assertEqual(parser.url("/foo/:bar/bar", {"bar": "foo"}), "https://api.acme.com/foo/foo/bar")
        self.assertEqual(parser.url("/foo/$bar<[0-9]+>/bar", {"bar": "foo"}), "https://api.acme.com/foo/foo/bar")
        self.assertEqual(parser.url("/foo/$bar/bar", {"bar": "foo"}), "https://api.acme.com/foo/foo/bar")
        self.assertEqual(parser.url("/foo/{bar}/bar", {"bar": "foo"}), "https://api.acme.com/foo/foo/bar")

        self.assertEqual(parser.url("/foo/:bar", {"bar": None}), "https://api.acme.com/foo/")
        self.assertEqual(parser.url("/foo/:bar", {"bar": 1337}), "https://api.acme.com/foo/1337")
        self.assertEqual(parser.url("/foo/:bar", {"bar": 13.37}), "https://api.acme.com/foo/13.37")
        self.assertEqual(parser.url("/foo/:bar", {"bar": True}), "https://api.acme.com/foo/1")
        self.assertEqual(parser.url("/foo/:bar", {"bar": False}), "https://api.acme.com/foo/0")
        self.assertEqual(parser.url("/foo/:bar", {"bar": "foo"}), "https://api.acme.com/foo/foo")

    def test_query(self):
        parser = Parser("https://api.acme.com/")

        test = TestObject(None, "foo")

        parameters = {
            "null": None,
            "int": 1337,
            "float": 13.37,
            "true": True,
            "false": False,
            "string": "foo",
            "date": datetime.date(2023, 2, 21),
            "datetime": datetime.datetime(2023, 2, 21, 19, 19, 0),
            "time": datetime.time(19, 19, 0),
            "args": test,
        }

        result = parser.query(parameters, ["args"])

        self.assertEqual(result["int"], "1337")
        self.assertEqual(result["float"], "13.37")
        self.assertEqual(result["true"], "1")
        self.assertEqual(result["false"], "0")
        self.assertEqual(result["string"], "foo")
        self.assertEqual(result["date"], "2023-02-21")
        self.assertEqual(result["datetime"], "2023-02-21T19:19:00Z")
        self.assertEqual(result["time"], "19:19:00")
        self.assertEqual(result["name"], "foo")


if __name__ == '__main__':
    unittest.main()
