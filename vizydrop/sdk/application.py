from vizydrop.sdk.account import AppOAuthv1Account, AppOAuthv2Account


class Application(object):
    """
    Base class for all externally connected applications
    """
    class Meta:
        name = None
        website = None
        logo = None
        description = None
        tags = []
        authentication = []
        sources = []

    @classmethod
    def get_auth(cls, identifier):
        """
        Get an app's auth class by its identifier
        :param identifier: auth identifier
        :return: class
        """
        for c in cls.Meta.authentication:
            if identifier.startswith('oauth'):
                if identifier == 'oauth' and issubclass(c, AppOAuthv1Account):
                    return c
                elif identifier == 'oauth2' and issubclass(c, AppOAuthv2Account):
                    return c
            elif getattr(c.Meta, 'identifier', None) == identifier:
                return c
        return None

    @classmethod
    def get_source(cls, identifier):
        """
        Gets an app's source class by its identifier
        :param identifier: source identifier
        :return: class
        """
        for c in cls.Meta.sources:
            if c.Meta.identifier == identifier:
                return c
        return None