import os
import tempfile
import unittest

import sketchingpy.local_data_struct


class LocalDataLayerTests(unittest.TestCase):

    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._dir.cleanup()

    def test_csv(self):
        path = os.path.join(self._dir.name, 'test.csv')
        test_data = [
            {'name': 'a', 'value': 1},
            {'name': 'b', 'value': 2}
        ]

        data_layer = sketchingpy.local_data_struct.LocalDataLayer()
        data_layer.write_csv(test_data, ['name', 'value'], path)

        loaded_data = data_layer.get_csv(path)
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]['name'], 'a')
        self.assertEqual(int(loaded_data[0]['value']), 1)
        self.assertEqual(loaded_data[1]['name'], 'b')
        self.assertEqual(int(loaded_data[1]['value']), 2)

    def test_json(self):
        path = os.path.join(self._dir.name, 'test.json')
        test_data = {'name': 'a', 'value': 1}

        data_layer = sketchingpy.local_data_struct.LocalDataLayer()
        data_layer.write_json(test_data, path)

        loaded_data = data_layer.get_json(path)
        self.assertEqual(loaded_data['name'], 'a')
        self.assertEqual(loaded_data['value'], 1)

    def test_text(self):
        path = os.path.join(self._dir.name, 'test.txt')
        test_data = 'test'

        data_layer = sketchingpy.local_data_struct.LocalDataLayer()
        data_layer.write_text(test_data, path)

        loaded_data = data_layer.get_text(path)
        self.assertEqual(loaded_data, 'test')
