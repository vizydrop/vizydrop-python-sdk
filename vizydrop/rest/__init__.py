import json
import sys
from traceback import format_tb
from datetime import datetime, date

from bson import ObjectId

from tornado import log
from tornado.web import RequestHandler
from tornado.httpclient import HTTPError

from vizydrop.fields import FieldedObject


class TpaHandlerMixin:
    @property
    def tpa(self):
        return self.settings.get('tpa')


class VzdJSONEncoder(json.JSONEncoder):
    """
    JSON encoder that understands ObjectID
    """

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, bytes):
            return o.decode('utf-8')
        elif isinstance(o, datetime) or isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, FieldedObject):
            return o.json_repr(include_class=True, include_id=True)
        elif isinstance(o, HTTPError):
            return str(o)

        return super(VzdJSONEncoder, self).default(o)


class VizydropAppRequestHandler(RequestHandler):
    _json_data = None

    @property
    def json_data(self):
        """
        JSON-parses request data and returns data as a dict
        :return: dict
        """
        if not self._json_data:
            try:
                return json.loads(self.request.body.decode('utf-8'))
            except ValueError:
                return {}
        return self._json_data

    def _handle_request_exception(self, e):
        """
        Handles an exception when processing a request, returns a formatted traceback in JSON
        :param e: exception
        :return:
        """
        if hasattr(e, 'HTTP_STATUS'):
            self.set_status(e.HTTP_STATUS)
        else:
            self.set_status(500)
        typ, exc, tb = sys.exc_info()
        log.app_log.error("Error: {}\n{}".format(str(exc), "".join(format_tb(tb))))
        self.finish(json.dumps({"exception": typ.__name__, "message": str(exc), 'traceback': format_tb(tb, None)}))

    def finish(self, chunk=None, encode=True):
        if not isinstance(chunk, str) and encode is True:
            chunk = json.dumps(chunk, cls=VzdJSONEncoder)
        super(VizydropAppRequestHandler, self).finish(chunk)
