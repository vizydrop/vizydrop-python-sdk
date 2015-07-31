import json

from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from tornado import gen

from vizydrop.sdk.source import DataSource
from .filter import BlankFilter
from .schema import ApiExampleSchema


class ApiExampleSource(DataSource):
    class Meta:
        identifier = "views"
        name = "Views"
        tags = ["view", ]
        description = "Views available in the Consumer Complaints Database"
        filter = BlankFilter

    class Schema(ApiExampleSchema):
        pass

    @classmethod
    @gen.coroutine
    def get_data(cls, account, source_filter, limit=100, skip=0):
        """
        Actually gathers the file
        """
        client = AsyncHTTPClient()

        uri = 'http://data.consumerfinance.gov/api/views.json'

        req = HTTPRequest(uri)
        resp = yield client.fetch(req)

        data = json.loads(resp.body.decode('utf-8'))

        # this helper function will "format" our data according to the schema we've specified above
        formatted = cls.format_data_to_schema(data)

        return json.dumps(formatted)
