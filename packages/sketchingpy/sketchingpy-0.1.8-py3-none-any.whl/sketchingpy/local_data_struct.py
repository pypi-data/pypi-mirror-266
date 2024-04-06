"""Implementation of data_struct for Sketch2DStatic and Sketch2DApp.

License:
    BSD
"""

import csv
import io
import json
import typing
import urllib.request

import sketchingpy.data_struct


class LocalDataLayer(sketchingpy.data_struct.DataLayer):
    """Implementation of DataLayer for desktop environment."""

    def get_csv(self, path: str) -> sketchingpy.data_struct.Records:
        if self._is_remote(path):
            with urllib.request.urlopen(path) as response:
                decoded = response.read().decode('utf-8')
                decoded_io = io.StringIO(decoded)
                reader = csv.DictReader(decoded_io)
                rows = list(reader)
        else:
            with open(path) as f:
                rows = list(csv.DictReader(f))

        return rows

    def write_csv(self, records: sketchingpy.data_struct.Records,
        columns: sketchingpy.data_struct.Columns, path: str):
        def build_record(target: typing.Dict) -> typing.Dict:
            return dict(map(lambda key: (key, target[key]), columns))

        records_serialized = map(build_record, records)

        with open(path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=columns)  # type: ignore
            writer.writeheader()
            writer.writerows(records_serialized)

    def get_json(self, path: str):
        if self._is_remote(path):
            with urllib.request.urlopen(path) as response:
                decoded = response.read().decode('utf-8')
                target = json.loads(decoded)
        else:
            with open(path) as f:
                target = json.load(f)

        return target

    def write_json(self, target, path: str):
        with open(path, 'w') as f:
            json.dump(target, f)

    def get_text(self, path: str) -> str:
        if self._is_remote(path):
            with urllib.request.urlopen(path) as response:
                text = response.read().decode('utf-8')
        else:
            with open(path) as f:
                text = f.read()

        return text

    def write_text(self, target: str, path: str):
        with open(path, 'w') as f:
            f.write(target)

    def _is_remote(self, path: str) -> bool:
        return path.startswith('http://') or path.startswith('https://')
