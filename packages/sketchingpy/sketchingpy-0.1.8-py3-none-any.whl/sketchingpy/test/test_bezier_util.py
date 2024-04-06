import unittest

import sketchingpy.bezier_util


class BezierUtil(unittest.TestCase):

    def test_bezier(self):
        bezier_maker = sketchingpy.bezier_util.BezierMaker()
        bezier_maker.add_point(1, 2)
        bezier_maker.add_point(3, 4)
        bezier_maker.add_point(5, 6)
        bezier_maker.add_point(7, 8)

        points = bezier_maker.get_points(100)

        self.assertEqual(len(points), 100)
        self.assertEqual(points[0][0], 1)
        self.assertEqual(points[0][1], 2)
        self.assertEqual(points[-1][0], 7)
        self.assertEqual(points[-1][1], 8)
