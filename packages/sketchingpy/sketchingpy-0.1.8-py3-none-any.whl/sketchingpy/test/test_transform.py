import math
import unittest

import sketchingpy.transform


class TransformTests(unittest.TestCase):

    def test_noop(self):
        transformer = sketchingpy.transform.Transformer()
        
        transformed_point = transformer.transform(5, 10)
        self.assertEqual(transformed_point.get_x(), 5)
        self.assertEqual(transformed_point.get_y(), 10)
        self.assertEqual(transformed_point.get_scale(), 1)
        self.assertEqual(transformed_point.get_rotation(), 0)

    def test_translate(self):
        transformer = sketchingpy.transform.Transformer()
        transformer.translate(2, 3)
        
        transformed_point = transformer.transform(5, 10)
        self.assertEqual(transformed_point.get_x(), 7)
        self.assertEqual(transformed_point.get_y(), 13)
        self.assertEqual(transformed_point.get_scale(), 1)
        self.assertEqual(transformed_point.get_rotation(), 0)

    def test_scale(self):
        transformer = sketchingpy.transform.Transformer()
        transformer.rotate(-1 * math.pi / 2)
        
        transformed_point = transformer.transform(5, 0)
        self.assertAlmostEqual(transformed_point.get_x(), 0)
        self.assertAlmostEqual(transformed_point.get_y(), 5)
        self.assertEqual(transformed_point.get_scale(), 1)
        self.assertAlmostEqual(transformed_point.get_rotation(), -1 * math.pi / 2)

    def test_rotate(self):
        pass
