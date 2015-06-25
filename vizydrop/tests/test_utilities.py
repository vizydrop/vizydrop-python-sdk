import unittest
from vizydrop.utils import *


class UtilityFunctionsTests(unittest.TestCase):
    def test_pluralize(self):
        self.assertEqual(pluralize("ship"), "ships")
        self.assertEqual(pluralize("account"), "accounts")
        self.assertEqual(pluralize("canary"), "canaries")

    def test_camelcase(self):
        self.assertEqual(convert_camel_to_underscore("CamelCasedStuff"), "camel_cased_stuff")
        self.assertEqual(convert_camel_to_underscore("AllYourBase"), "all_your_base")

    def test_link_header_parser(self):
        header_contents = '<https://api.github.com/user/repos?page=3&per_page=100>; ' \
                          'rel="next", <https://api.github.com/user/repos?page=50&per_page=100>; rel="last"'

        result = parse_link_header(header_contents)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.__len__(), 2)
        self.assertIn("next", result.keys())
        self.assertIn("last", result.keys())
        self.assertEqual(result.get('next'), 'https://api.github.com/user/repos?page=3&per_page=100')
        self.assertEqual(result.get('last'), 'https://api.github.com/user/repos?page=50&per_page=100')