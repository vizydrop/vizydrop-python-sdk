from . import FlatFileExampleTestCase


class FlatFileExampleAppDetailsTests(FlatFileExampleTestCase):
    def test_app_info(self):
        response = self.GET('/')

        self.assertHttpOk(response)
        self.assertInfoResponseValid(response)
