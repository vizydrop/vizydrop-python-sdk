from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
import unittest

from vizydrop import fields


class FieldTypeTests(unittest.TestCase):
    def test_url_field_valid_checks(self):
        field = fields.URLField()
        field.set('https://www.google.com/')
        self.assertTrue(field.is_valid())
        field.set('http://www.targetprocess.com/')
        self.assertTrue(field.is_valid())
        field.set('qwerty://keyboards.stuff.words.org/')
        self.assertFalse(field.is_valid())
        field.set('https://www.g@@gle.com/')
        self.assertFalse(field.is_valid())

    def test_list_field_basics(self):
        field = fields.MultiListField()
        field.add(1)
        field.add(2)
        field.add(3)
        self.assertEqual(3, field.__len__())