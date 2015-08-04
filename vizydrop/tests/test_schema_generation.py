import unittest
from vizydrop.fields import *
from vizydrop.sdk.source import SourceSchema, DataSource, SourceFilter


class TestFilter(SourceFilter):
    simple_string = TextField(name="String", description="A Simple String")

    def simple_datalist_function(account, **kwargs):
        pass

    def parameter_datalist_function(account, simple_string, **kwargs):
        pass

    dl_item = TextField(name="Datalist Item 1", description="A simple datalist function",
                        get_options=simple_datalist_function)
    dl_item2 = TextField(name="Datalist Item 2", description="A datalist function with a required parameter",
                         get_options=parameter_datalist_function)


class TestObject(DataSource):
    class Schema(SourceSchema):
        text_field = TextField(name="Text Field")
        date_field = DateField(name="Date Field")

    class Meta:
        identifier = "test"
        description = "Test"
        tags = []
        name = "Test"
        filter = TestFilter


class SchemaGenerationTest(unittest.TestCase):
    def test_all_fields_included(self):
        schema = TestObject.get_schema()
        keys = schema.keys()
        for item in ['filter', 'name', 'tags', 'id' ,'fields']:
            self.assertIn(item, keys)

    def test_filter_schema(self):
        schema = TestObject.get_schema()
        self.assertIsInstance(schema['filter'], list)
        fields = [field['id'] for field in schema['filter']]
        for item in ['simple_string', 'dl_item', 'dl_item2']:
            self.assertIn(item, fields)

    def test_datalist_inspections(self):
        schema = TestObject.get_schema()
        simple_datalist = None
        advanced_datalist = None

        # grab our two fields out of the list
        for field in schema['filter']:
            if field['id'] == 'dl_item':
                simple_datalist = field
            elif field['id'] == 'dl_item2':
                advanced_datalist = field

        # we should have both fields
        self.assertIsNotNone(simple_datalist)
        self.assertIsNotNone(advanced_datalist)
        # both should have datalist: True
        self.assertTrue(simple_datalist['datalist'])
        self.assertTrue(advanced_datalist['datalist'])
        # simple should have no requires
        self.assertEqual(simple_datalist['datalist_requires'], [])
        # advanced should have a requires
        self.assertEqual(advanced_datalist['datalist_requires'], ['simple_string'])

    def test_source_schema(self):
        schema = TestObject.get_schema()

        self.assertIsInstance(schema['fields'], dict)

        self.assertIn('text_field', schema['fields'].keys())
        self.assertIn('date_field', schema['fields'].keys())

    def test_date_field_always_datalist(self):
        schema = TestObject.get_schema()
        self.assertTrue(schema['fields']['date_field']['datalist'])