from . import ApiExampleTestCase


class ApiExampleAppDetailsTests(ApiExampleTestCase):
    def test_app_info(self):
        response = self.GET('/')

        self.assertHttpOk(response)
        self.assertInfoResponseValid(response)
