import json

from . import ApiExampleTestCase


class ApiExampleSourceTests(ApiExampleTestCase):
    def test_get_source(self):
        response = self.POST('/', data=json.dumps({"source": "views",
                                                   "account": {"auth": "none"},
                                                   "filter": {}}))

        self.assertHttpOk(response)