from vizydrop.sdk.application import Application
from .auth import NoAuth
from .source import ApiExampleSource


class ApiExample(Application):
    class Meta:
        version = "1.0"
        name = "External API Example"
        website = "http://www.vizydrop.com/"
        color = "#FF9900"
        description = "This is just an API example from the Vizydrop Python SDK."
        tags = ['example', 'api', ]

        authentication = [NoAuth, ]

        sources = [ApiExampleSource, ]
