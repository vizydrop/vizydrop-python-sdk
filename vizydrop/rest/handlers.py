from .base import BaseHandler
from .account import AccountValidationHandler, OAuth1AccountHandler, OAuth2AccountHandler
from .filter import FilterDatalistHandler

rest_handlers = [
    (r'^/?$', BaseHandler),
    (r'^/datalist/?$', FilterDatalistHandler),
    (r'^/oauth1/?$', OAuth1AccountHandler),
    (r'^/oauth2/?$', OAuth2AccountHandler),
    (r'^/validate/?$', AccountValidationHandler)
]
