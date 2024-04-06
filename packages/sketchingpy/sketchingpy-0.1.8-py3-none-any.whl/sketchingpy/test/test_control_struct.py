import unittest

import sketchingpy.control_struct


class ControlStructTest(unittest.TestCase):

    def test_button(self):
        button = sketchingpy.control_struct.Button('test')
        self.assertEqual(button.get_name(), 'test')
