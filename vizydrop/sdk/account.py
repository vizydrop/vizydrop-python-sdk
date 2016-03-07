import base64

from oauthlib import oauth1, oauth2
from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPRequest

from vizydrop.fields import *
from tornado import gen, log
import json
from datetime import datetime, timedelta


class Account(FieldedObject):
    """
    Base class for authentication schemes defined in application packages
    """

    class Meta:
        identifier = None
        description = None
        name = None

    @classmethod
    def get_field_data(cls):
        """Gets field information for this authentication scheme required to create an Account object"""
        fields = []
        for name, field in cls.get_all_fields():
            f = {"id": name}
            f.update(field.get_api_description())
            if f.get('description', None) and f.get('name', None):
                # only include fields with descriptions and titles
                fields.append(f)
        return fields

    @classmethod
    def get_schema(cls):
        """
        Gets the authorization schema
        """
        schema = {
            "name": cls.Meta.name,
            "description": cls.Meta.description,
            "fields": cls.get_field_data()
        }
        if issubclass(cls, AppOAuthv1Account):
            schema.update({"id": "oauth"})
        elif issubclass(cls, AppOAuthv2Account):
            schema.update({"id": "oauth2"})
        else:
            schema.update({"id": cls.Meta.identifier})
        return schema

    def get_request(self, url):
        """
        Get a HTTPRequest object for a specified URL with all authentication parameters handled
        :param url: str URL of the request
        :return: HTTPRequest
        """
        raise NotImplementedError

    def validate(self):
        """
        Validates the connection of the account
        :return: bool
        """
        raise NotImplementedError

    def get_friendly_name(self):
        """
        Generate a friendly name for an account
        :return:
        """
        raise NotImplementedError


class AppHTTPBasicAuthAccount(Account):
    username = TextField(name='Username', optional=False, description='Your username')
    password = PasswordField(name='Password', optional=False, description='Your password', protected=True)

    def _get_basic_auth(self):
        """
        Returns the base64 representation of username:password
        """
        return base64.b64encode(":".join([self.username, self.password]).encode('utf-8')).decode('utf-8')


class AppOAuthAccount(Account):
    """
    Base class for OAuth-based authentication schemes (all versions)
    """

    @classmethod
    def get_field_data(cls):
        """Returns simple OAuth scheme information"""
        return [
            {
                "id": "redirect_uri",
                "title": "redirect_uri",
                "description": "OAuth post-auth redirect URI",
                "type": "oauth"
            }
        ]


class AppOAuthv1Account(AppOAuthAccount):
    """
    Base class for OAuth (v1)-based authentication schemes defined in application packages
    """

    class Meta:
        client_key = None
        client_secret = None
        request_token_uri = None
        access_token_uri = None
        authorize_token_uri = None

    _oauth_client = None

    def get_client(self):
        """
        Get the OAuth v1 client for this authentication scheme
        :return: oauthlib.oauth1.Client
        """
        if not self._oauth_client:
            self._oauth_client = oauth1.Client(self.Meta.client_key, client_secret=self.Meta.client_secret)
        if self.access_secret:
            self._oauth_client.resource_owner_secret = self.access_secret
            self._oauth_client.resource_owner_key = self.access_token
        return self._oauth_client

    def get_authorize_uri(self, token):
        raise NotImplemented

    access_token = TextField(name="OAuth Access Token", protected=True)
    access_secret = TextField(name="OAuth Secret Token", protected=True)


class AppOAuthv2Account(AppOAuthAccount):
    """
    Base class for OAuth (v2)-based authentication schemes defined in application packages
    """

    class Meta:
        client_id = None
        client_secret = None
        token_placement = None
        token_type = None

        scope = None

        auth_uri = None
        token_uri = None

    _oauth_client = None

    def get_client(self):
        """
        Gets the OAuth v2 client for this authentication scheme
        :return: oauthlib.oauth2.Client
        """
        if not self._oauth_client:
            self._oauth_client = oauth2.WebApplicationClient(self.Meta.client_id,
                                                             default_token_placement=self.Meta.token_placement,
                                                             token_type=self.Meta.token_type, scope=self.Meta.scope)

        if self.callback_uri:
            self._oauth_client.redirect_url = self.callback_uri

        if self.access_token:
            self._oauth_client.access_token = self.access_token

        return self._oauth_client

    def finish_setup(self, provider_response):
        """
        Handles setting up the rest of the OAuth token given the input response from the endpoint/provider
        This method must be overridden by all subclasses
        :param provider_response:
        :return:
        """
        raise NotImplementedError

    @gen.coroutine
    def do_token_refresh(self):
        # check refreshes
        if hasattr(self, 'refresh_token'):
            # and actually refresh if we need it
            if self.token_expiration and self.token_expiration < datetime.now():
                log.app_log.info("Refreshing token for account {}".format(self._id))
                try:
                    uri, headers, body = self.get_client().prepare_refresh_token_request(self.Meta.token_uri,
                                                                                         client_id=self.Meta.client_id,
                                                                                         client_secret=self.Meta.client_secret,
                                                                                         refresh_token=self.refresh_token)

                    token_request = HTTPRequest(uri, body=body.encode('utf-8'), headers=headers, method='POST')
                    client = AsyncHTTPClient()
                    response = yield client.fetch(token_request)

                    response_data = json.loads(response.body.decode('utf-8'))
                    self.access_token = response_data.get('access_token')
                    self._oauth_client.access_token = self.access_token
                    self.token_expiration = datetime.now() + timedelta(seconds=int(response_data.get('expires_in')))
                    if 'refresh_token' in response_data.keys():
                        self.refresh_token = response_data.get('refresh_token')
                    log.app_log.info("Token refreshed successfully!")
                except HTTPError as e:
                    log.app_log.error("Error refreshing token {} ({})".format(self._id, e.readlines()))
                    return False, e.response.reason
        return True, None

    access_token = TextField(name="OAuth Access Token")
    callback_uri = TextField(name="Redirect/callback URI")
