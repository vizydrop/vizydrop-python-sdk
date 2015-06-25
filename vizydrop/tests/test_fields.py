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

    def test_range_field_basics(self):
        field = fields.RangeField()
        field.set('a,b')
        self.assertEqual(field.low(), 'a')
        self.assertEqual(field.high(), 'b')
        self.assertRaises(ValueError, field.set, ['a', 'b', 'c'])
        field.set(['all', 'your base'])
        self.assertEqual(field.low(), 'all')
        self.assertEqual(field.high(), 'your base')

    def test_date_range_field(self):
        field = fields.DateRangeField()
        field.set('2014-01-01,2015-01-01')
        self.assertIsInstance(field.low(), date)
        self.assertEqual(field.low(), date(2014, 1, 1))
        self.assertIsInstance(field.high(), date)
        self.assertEqual(field.high(), date(2015, 1, 1))

    def test_datetime_range_field(self):
        field = fields.DateTimeRangeField()
        field.set('2014-01-01T12:34:56-0400,2015-01-01T01:23:45-0400')
        self.assertIsInstance(field.low(), datetime)
        self.assertEqual(field.low(), datetime(2014, 1, 1, 12, 34, 56, tzinfo=timezone(timedelta(-1, 72000))))
        self.assertIsInstance(field.high(), datetime)
        self.assertEqual(field.high(), datetime(2015, 1, 1, 1, 23, 45, tzinfo=timezone(timedelta(-1, 72000))))

    def test_decimal_range_field(self):
        field = fields.DecimalRangeField()
        field.set('0.002,3.14159265359')
        self.assertIsInstance(field.low(), Decimal)
        self.assertAlmostEqual(field.low(), Decimal(0.002), 4)
        self.assertIsInstance(field.high(), Decimal)
        self.assertAlmostEqual(field.high(), Decimal(3.14159265359), 12)
