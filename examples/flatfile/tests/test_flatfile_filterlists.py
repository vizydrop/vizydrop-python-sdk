from . import FlatFileExampleTestCase
import json
import os


class FlatFileExampleFilterTests(FlatFileExampleTestCase):
    def test_filter_filelist(self):
        response = self.POST('/datalist?source=file&field=file', data=json.dumps({"auth": "none"}))

        self.assertHttpOk(response)
        json_resp = self.json_resp(response)
        self.assertIsInstance(json_resp, list)
        files = []

        for item in json_resp:
            self.assertIn('value', item.keys())
            self.assertIn('title', item.keys())
            files.append(item['value'])

        # check to be sure all files were included
        data_dir = os.path.join(os.path.dirname(__file__), '../data')
        data_files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
        for data_file in data_files:
            self.assertIn(data_file, files)