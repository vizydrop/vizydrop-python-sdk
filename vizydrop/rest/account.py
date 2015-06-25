from http.client import UNAUTHORIZED, BAD_REQUEST, INTERNAL_SERVER_ERROR, ACCEPTED, NOT_ACCEPTABLE
import json
import re
from tornado.concurrent import Future
from tornado.gen import coroutine
from tornado import log
from tornado.web import asynchronous
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError

from . import TpaHandlerMixin, VizydropAppRequestHandler
from vizydrop.sdk.account import AppOAuthv1Account, AppOAuthv2Account


class AccountValidationHandler(VizydropAppRequestHandler, TpaHandlerMixin):
    @coroutine
    @asynchronous
    def post(self):
        identifier = self.json_data.get('id')
        fields = self.json_data.get('fields')
        auth_type = self.tpa.get_auth(identifier)
        account = auth_type(fields)
        result, errors = yield account.validate()
        if result:
            if account.name is None:
                friendly_name = account.get_friendly_name()
                if isinstance(friendly_name, Future):
                    friendly_name = yield friendly_name
                account.name = friendly_name
            self.finish(account)
        else:
            self.set_status(UNAUTHORIZED)
            self.finish({"error": errors})


class OAuth1AccountHandler(VizydropAppRequestHandler, TpaHandlerMixin):
    @coroutine
    def get(self):
        auth = self.tpa.get_auth('oauth')
        if not issubclass(auth, AppOAuthv1Account):
            self.set_status(BAD_REQUEST)
            return self.finish({"error": "incompatible authentication type for OAuth"})
        auth = auth()  # instantiate that sucker
        client = auth.get_client()
        callback_uri = self.get_query_argument('callback_uri', None)
        if callback_uri is None:
            raise ValueError("missing required param 'callback_uri'")
        client.callback_uri = callback_uri
        uri, headers, body = client.sign(auth.Meta.request_token_uri)
        token_req = HTTPRequest(auth.Meta.request_token_uri, headers=headers, body=body)
        http_client = AsyncHTTPClient()
        try:
            response = yield http_client.fetch(token_req)
        except HTTPError as e:
            self.set_status(e.response.code)
            self.finish({
                "code": e.code,
                "reason": e.response.reason,
                "error": e.response.body.decode('utf-8')
            })
            return

        regex = re.compile("oauth_token=(?P<token>[a-z0-9]+)&oauth_token_secret=(?P<secret>[a-z0-9]+)")
        r = regex.search(response.body.decode('utf-8'))
        try:
            token, secret = r.groups()
        except AttributeError:
            self.set_status(INTERNAL_SERVER_ERROR)
            self.finish(response.body.decode('utf-8'))
            return
        self.set_status(ACCEPTED)
        self.finish({"secret": secret, "token": token,
                     "redirect_uri": auth.get_authorize_uri(token)})

    @coroutine
    def post(self):
        auth = self.tpa.get_auth('oauth')
        if not issubclass(auth, AppOAuthv1Account):
            self.set_status(BAD_REQUEST)
            return self.finish({"error": "incompatible authentication type for OAuth"})
        auth = auth()  # instantiate!
        fields = self.json_data.get('fields')
        auth.update(fields)
        client = auth.get_client()
        verifier = self.json_data.get('oauth_verifier', None)
        if verifier is None:
            self.set_status(BAD_REQUEST)
            return self.finish({"error": "missing required parameter oauth_verifier"})
        client.verifier = verifier
        uri, headers, body = client.sign(auth.Meta.access_token_uri)
        http_client = AsyncHTTPClient()
        token_req = HTTPRequest(uri, headers=headers, body=body)
        try:
            response = yield http_client.fetch(token_req)
        except HTTPError as e:
            self.set_status(e.response.code)
            self.finish({
                "code": e.code,
                "reason": e.response.reason,
                "error": e.response.body.decode('utf-8')
            })
            return

        regex = re.compile("oauth_token=(?P<token>[a-z0-9]+)&oauth_token_secret=(?P<secret>[a-z0-9]+)")
        r = regex.search(response.body.decode('utf-8'))
        try:
            token, secret = r.groups()
        except AttributeError:
            self.set_status(INTERNAL_SERVER_ERROR)
            return self.finish('internal server error')
        auth.access_secret = secret
        auth.access_token = token
        success, errors = yield auth.validate()
        if success:
            self.set_status(ACCEPTED)
            self.finish(auth)
        else:
            self.set_status(NOT_ACCEPTABLE)
            log.app_log.error("Unable to complete OAuth account: {}".format('\n'.join(errors)))
            self.finish({"errors": errors})


class OAuth2AccountHandler(VizydropAppRequestHandler, TpaHandlerMixin):
    def get(self):
        auth = self.tpa.get_auth('oauth2')
        if not issubclass(auth, AppOAuthv2Account):
            self.set_status(BAD_REQUEST)
            return self.finish({"error": "incompatible authentication type for OAuthV2"})
        auth = auth()  # instantiate that sucker
        client = auth.get_client()
        callback_uri = self.get_query_argument('callback_uri', None)
        if callback_uri is None:
            raise ValueError("missing required param 'callback_uri'")
        # load any extra query arguments (e.g. id passthrough for google sheets)
        query = self.get_query_argument('query', None)
        if query is not None:
            query = json.loads(query)
        else:
            # if we have no extra query arguments, to avoid errors below we have to pass an empty dict as **query
            query = {}
        if 'additional_request_parameters' in auth.Meta.__dict__.keys():
            query.update(auth.Meta.additional_request_parameters)
        uri, headers, body = client.prepare_authorization_request(auth.Meta.auth_uri,
                                                                  redirect_url=callback_uri,
                                                                  scope=auth.Meta.scope,
                                                                  **query)
        auth.callback_uri = callback_uri
        self.set_status(ACCEPTED)
        self.finish({"redirect_uri": uri, "callback_uri": callback_uri})

    @coroutine
    def post(self):
        auth = self.tpa.get_auth('oauth2')
        if not issubclass(auth, AppOAuthv2Account):
            self.set_status(BAD_REQUEST)
            return self.finish({"error": "incompatible authentication type for OAuthV2"})
        auth = auth()  # instantiate!
        fields = self.json_data.get('fields')
        auth.update(fields)
        client = auth.get_client()
        client.code = self.json_data.get('code')
        client.state = self.json_data.get('state')

        uri, headers, body = client.prepare_token_request(auth.Meta.token_uri,
                                                          client_secret=auth.Meta.client_secret)
        http_client = AsyncHTTPClient()
        token_req = HTTPRequest(uri, headers=headers, body=body, method='POST')
        try:
            response = yield http_client.fetch(token_req)
        except HTTPError as e:
            log.app_log.error("OAuth2 Request Error {}:\n{}".format(e.code, e.response.body.decode('utf-8')))
            self.set_status(e.response.code)
            self.finish({
                "code": e.code,
                "reason": e.response.reason,
                "error": e.response.body.decode('utf-8')
            })
            return

        auth.finish_setup(response)
        success, errors = yield auth.validate()
        if success:
            self.set_status(ACCEPTED)
            self.finish(auth)
        else:
            self.set_status(NOT_ACCEPTABLE)
            self.finish({"errors": errors})
