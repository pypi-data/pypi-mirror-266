import os.path
import unittest

import sketchingpy.abstracted
import sketchingpy.state_struct


class AbstractedTests(unittest.TestCase):

    def test_reorder_coords(self):
        output_coords = sketchingpy.abstracted.reorder_coords(1, 4, 2, 3)
        self.assertEqual(len(output_coords), 4)
        self.assertEqual(output_coords[0], 1)
        self.assertEqual(output_coords[1], 3)
        self.assertEqual(output_coords[2], 2)
        self.assertEqual(output_coords[3], 4)

    def test_get_font_name(self):
        assert os.path.sep in ['\\', '/']
        name = sketchingpy.abstracted.get_font_name(
            sketchingpy.state_struct.Font('a/b/test-1.otf', 12),
            '/'
        )

        self.assertEqual(name, '12px test-1')
