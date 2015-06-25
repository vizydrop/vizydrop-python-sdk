import unittest
from vizydrop.fields import FieldedObject, Field


class FieldedObjectTests(unittest.TestCase):
    def test_field_ordering(self):
        class TestClass(FieldedObject):
            one = Field()
            two = Field()
            three = Field()

        dict = TestClass.get_all_fields()

        self.assertEqual(['one', 'two', 'three'], [name for name, field in dict])

        for name, field in dict:
            self.assertTrue(issubclass(type(field), Field))

    def test_field_ordering_inheritance(self):
        class TestClassBase(FieldedObject):
            two = Field()
            three = Field()

        class TestClass(TestClassBase):
            one = Field()

        dict = TestClass.__ordered__

        self.assertIn('one', dict)
        self.assertIn('two', dict)
        self.assertIn('three', dict)

        dict = TestClass.get_all_fields()

        self.assertEqual(['one', 'two', 'three'], [name for name, field in dict])