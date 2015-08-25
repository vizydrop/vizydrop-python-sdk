from vizydrop.sdk.application import Application
from .auth import NoAuth
from .source import ApiExampleSource


class ApiExample(Application):
    class Meta:
        version = "1.0"
        name = "Paginated API Example"
        website = "http://www.vizydrop.com/"
        color = "#FF9900"
        description = "This is an advanced example of using toro queues for concurrent HTTP calls when leveraging the " \
                      "Vizydrop Python SDK"
        tags = ['example', 'api', 'concurrent' ]

        authentication = [NoAuth, ]

        sources = [ApiExampleSource, ]
