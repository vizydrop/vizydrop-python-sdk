from http.client import INTERNAL_SERVER_ERROR
import json

from vizydrop.rest import VizydropAppRequestHandler
from vizydrop.sdk.source import StreamingDataSource
from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from . import TpaHandlerMixin


class BaseHandler(VizydropAppRequestHandler, TpaHandlerMixin):
    def options(self):
        self.set_status(204)
        self.finish()

    def get(self):
        meta = self.tpa.Meta
        self.finish({
            "version": meta.version,
            "tags": meta.tags,
            "name": meta.name,
            "color": meta.color or None,
            "description": meta.description,
            "site": meta.website,
            "sources": [source.get_schema() for source in meta.sources],
            "authentication": [account.get_schema() for account in meta.authentication]
        })

    @coroutine
    def post(self):
        post_body = json.loads(self.request.body.decode('utf-8'))
        source = post_body.get('source')
        account_fields = post_body.get('account')
        account_identifier = account_fields.pop('auth')
        filter_fields = post_body.get('filter')
        limit = post_body.get('limit', 100)
        skip = post_body.get('skip', 0)

        account_type = self.tpa.get_auth(account_identifier)
        account = account_type(account_fields)
        source_type = self.tpa.get_source(source)
        filter = source_type.Meta.filter(filter_fields)

        if issubclass(source_type, StreamingDataSource):
            source_type.stream_callback = self.on_stream_data
            try:
                yield source_type.get_data(account, filter, limit=limit, skip=skip)
                self.flush()
                self.finish('')
            except HTTPError as e:
                raise e
            except Exception as e:
                self.set_status(INTERNAL_SERVER_ERROR)
                self._handle_request_exception(e)
        else:
            try:
                data = yield source_type.get_data(account, filter, limit=limit, skip=skip)
                self.finish(data, encode=False)
            except HTTPError as e:
                raise e
            except Exception as e:
                self.set_status(INTERNAL_SERVER_ERROR)
                self._handle_request_exception(e)

    def on_stream_data(self, data):
        self.write(data)
        self.flush()
