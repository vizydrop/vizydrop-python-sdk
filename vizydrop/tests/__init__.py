import json

from tornado.httpclient import HTTPRequest, HTTPResponse
from tornado import testing
from tornado.ioloop import IOLoop


class AppTestCase(testing.AsyncHTTPTestCase):
    def get_new_ioloop(self):
        return IOLoop.instance()

    def get_app(self):
        raise NotImplementedError

    def json_resp(self, response):
        return json.loads(response.body.decode('utf-8'))

    def assertHttpOk(self, response):
        self.assertIsNone(response.error, msg=response.body.decode('utf-8'))

    def assertInfoResponseValid(self, response):
        if isinstance(response, HTTPResponse):
            response = json.loads(response.body.decode('utf-8'))

        self.assertIsInstance(response, dict)
        keys = response.keys()

        for key in ['color', 'tags', 'description', 'sources', 'site', 'name', 'authentication']:
            self.assertIn(key, keys)

        for source in response.get('sources'):
            keys = source.keys()
            for key in ['id', 'name', 'description', 'tags', 'fields']:
                self.assertIn(key, keys)

        for auth in response.get('authentication'):
            keys = auth.keys()
            for key in ['id', 'name', 'description', 'fields']:
                self.assertIn(key, keys)

    def get_request(self, url, method='GET', body=None, headers=None):
        url = self.get_url(url)
        req = HTTPRequest(url, method=method, body=body)
        req.headers['Content-Type'] = 'application/json; charset=UTF-8'
        if headers:
            req.headers.update(headers)
        return req

    def GET(self, url):
        req = self.get_request(url)
        self.http_client.fetch(req, self.stop, request_timeout=15, response_timeout=30)
        return self.wait(timeout=30)

    def POST(self, url, data=None):
        req = self.get_request(url, method='POST', body=data)
        self.http_client.fetch(req, self.stop, request_timeout=15, response_timeout=30)
        return self.wait(timeout=30)

    def PUT(self, url, data=None):
        req = self.get_request(url, method='PUT', body=data)
        self.http_client.fetch(req, self.stop, request_timeout=15, response_timeout=30)
        return self.wait(timeout=30)

    def DELETE(self, url):
        req = self.get_request(url, method='DELETE')
        self.http_client.fetch(req, self.stop, request_timeout=15, response_timeout=30)
        return self.wait(timeout=30)
