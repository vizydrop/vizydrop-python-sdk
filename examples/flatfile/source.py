from tornado.httpclient import AsyncHTTPClient
from tornado import gen
from vizydrop.sdk.source import DataSource, SourceSchema
from .filter import FileChooserFilter
import os

class FlatFileSource(DataSource):
    class Meta:
        identifier = "file"
        name = "File"
        tags = ["file", ]
        description = "Contents of a datafile"
        filter = FileChooserFilter

    class Schema(SourceSchema):
        pass

    @classmethod
    @gen.coroutine
    def get_data(cls, account, source_filter, limit=100, skip=0):
        """
        Actually gathers the file
        """
        client = AsyncHTTPClient()

        source_filter = FileChooserFilter(source_filter)

        if source_filter.file is None:
            raise ValueError('required parameter file missing')

        file_path = os.path.join(os.path.dirname(__file__), 'data', source_filter.file)
        if not os.path.isfile(file_path):
            raise ValueError('item at path {} is not a file'.format(file_path))

        with open(file_path, 'rb') as file:
            return file.read()