from vizydrop.sdk.application import Application
from .auth import NoAuth
from .source import FlatFileSource


class FlatFileExample(Application):
    class Meta:
        version = "1.0"
        name = "Flatfile Example"
        website = "http://www.vizydrop.com/"
        color = "#FF9900"
        description = "This is just a flatfile example from the Vizydrop Python SDK."
        tags = ['example', ]

        authentication = [NoAuth, ]

        sources = [FlatFileSource, ]
