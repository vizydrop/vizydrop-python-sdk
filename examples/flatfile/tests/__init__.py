from vizydrop.tests import AppTestCase
from vizydrop.tpa import VizydropTPAHost


class FlatFileExampleTestCase(AppTestCase):
    def get_app(self):
        app = VizydropTPAHost(app_module='examples.flatfile.app')
        return app