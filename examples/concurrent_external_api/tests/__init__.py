from vizydrop.tests import AppTestCase
from vizydrop.tpa import VizydropTPAHost


class ApiExampleTestCase(AppTestCase):
    def get_app(self):
        app = VizydropTPAHost(app_module='examples.concurrent_external_api.app')
        return app