import unittest

import sketchingpy.shape_struct


class ShapeStructTest(unittest.TestCase):

    def test_line(self):
        shape = sketchingpy.shape_struct.Shape(50, 100)
        shape.add_line_to(150, 200)
        shape.end()

        self.assertEqual(shape.get_start_x(), 50)
        self.assertEqual(shape.get_start_y(), 100)

        segments = shape.get_segments()
        segment = segments[0]
        self.assertEqual(segment.get_destination_x(), 150)
        self.assertEqual(segment.get_destination_y(), 200)

    def test_bezier(self):
        shape = sketchingpy.shape_struct.Shape(50, 100)
        shape.add_bezier_to(60, 110, 140, 190, 150, 200)
        shape.end()

        self.assertEqual(shape.get_start_x(), 50)
        self.assertEqual(shape.get_start_y(), 100)

        segments = shape.get_segments()
        segment = segments[0]
        self.assertEqual(segment.get_control_x1(), 60)
        self.assertEqual(segment.get_control_y1(), 110)
        self.assertEqual(segment.get_control_x2(), 140)
        self.assertEqual(segment.get_control_y2(), 190)
        self.assertEqual(segment.get_destination_x(), 150)
        self.assertEqual(segment.get_destination_y(), 200)

    def test_open(self):
        shape = sketchingpy.shape_struct.Shape(50, 100)
        shape.add_line_to(150, 200)
        shape.add_line_to(200, 250)
        shape.end()
        
        self.assertTrue(shape.get_is_finished())
        self.assertFalse(shape.get_is_closed())

    def test_closed(self):
        shape = sketchingpy.shape_struct.Shape(50, 100)
        shape.add_line_to(150, 200)
        shape.add_line_to(200, 250)
        shape.close()
        
        self.assertTrue(shape.get_is_finished())
        self.assertTrue(shape.get_is_closed())

    def test_inspect_early(self):
        shape = sketchingpy.shape_struct.Shape(50, 100)
        shape.add_line_to(150, 200)
        shape.add_line_to(200, 250)

        self.assertFalse(shape.get_is_finished())
        
        with self.assertRaises(RuntimeError):
            shape.get_is_closed()

    def test_get_bounds(self):
        shape = sketchingpy.shape_struct.Shape(50, 100)
        shape.add_line_to(150, 200)
        shape.add_line_to(200, 250)
        shape.end()
        
        self.assertEqual(shape.get_min_x(), 50)
        self.assertEqual(shape.get_min_y(), 100)
        self.assertEqual(shape.get_max_x(), 200)
        self.assertEqual(shape.get_max_y(), 250)