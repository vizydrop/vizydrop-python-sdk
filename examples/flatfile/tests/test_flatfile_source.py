import json

from . import FlatFileExampleTestCase


class FlatFileExampleSourceTests(FlatFileExampleTestCase):
    def test_filter_filelist(self):
        response = self.POST('/', data=json.dumps({"source": "file",
                                                   "account": {"auth": "none"},
                                                   "filter": {"file": "flowers.csv"}}))

        self.assertHttpOk(response)