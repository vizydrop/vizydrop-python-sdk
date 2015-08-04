from http.client import BAD_REQUEST, NOT_FOUND
import inspect

from tornado import gen
from tornado.httpclient import HTTPError
from . import VizydropAppRequestHandler, TpaHandlerMixin


class FilterDatalistHandler(VizydropAppRequestHandler, TpaHandlerMixin):
    @gen.coroutine
    def post(self):
        source_id = self.get_query_argument('source')
        field_name = self.get_query_argument('field')
        account = self.json_data
        account_id = account.get('auth', None)

        if account is None or account_id is None:
            self.set_status(BAD_REQUEST)
            return self.finish({"error": "account required"})

        auth = self.tpa.get_auth(account_id)(account)
        source = self.tpa.get_source(source_id)
        filter = source.Meta.filter

        if filter is None:
            self.set_status(BAD_REQUEST)
            return self.finish({"error": "no filter exists for source"})

        try:
            field = getattr(filter, field_name)
        except AttributeError:
            self.set_status(NOT_FOUND)
            return self.finish({"error": "filter field '{}' not found".format(field_name)})

        # check for required arguments to the get_options func
        get_func = field.get_options
        argspec = inspect.getargspec(get_func)

        args = []
        for arg in argspec[0][1:]:
            argval = self.get_query_argument(arg, None)
            if argval is None:
                self.set_status(BAD_REQUEST)
                return self.finish({"error": "missing required parameter '{}'".format(arg)})
            args.append(argval)

        try:
            options = yield gen.coroutine(get_func)(auth, *args, request=self.request)
            self.finish(options)
        except Exception as e:
            self.set_status(INTERNAL_SERVER_ERROR)
            self._handle_request_exception(e)
