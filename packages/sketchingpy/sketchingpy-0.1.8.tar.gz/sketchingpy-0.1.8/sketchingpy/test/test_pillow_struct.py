import unittest

import PIL.Image
import PIL.ImageDraw

import sketchingpy.const
import sketchingpy.pillow_struct
import sketchingpy.transform


class PillowStructTests(unittest.TestCase):

    def setUp(self):
        image = PIL.Image.new('RGBA', (1, 1), (255, 255, 255, 0))
        drawable = PIL.ImageDraw.Draw(image, 'RGBA')
        self._example_image = sketchingpy.pillow_struct.WritableImage(image, drawable)

    def test_rect(self):
        rect = sketchingpy.pillow_struct.Rect(1, 2, 4, 8)
        rect.set_center_x(10)
        rect.set_center_y(20)
        self.assertEqual(rect.get_x(), 8)
        self.assertEqual(rect.get_y(), 16)
    
    def test_transformed_writable(self):
        writable = sketchingpy.pillow_struct.TransformedWritable(self._example_image, 10, 20)
        
        derived_1 = writable.get_with_offset(5, 10)
        self.assertEqual(derived_1.get_x(), 15)
        self.assertEqual(derived_1.get_y(), 30)

        transformer = sketchingpy.transform.Transformer()
        transformer.translate(5, 10)

        derived_2 = writable.transform(transformer)
        self.assertEqual(derived_2.get_x(), 15)
        self.assertEqual(derived_2.get_y(), 30)
    
    def test_transformed_line(self):
        writable = sketchingpy.pillow_struct.TransformedLine(10, 20, 30, 40, '#C0C0C0', 1)
        
        derived_1 = writable.get_with_offset(5, 10)
        self.assertEqual(derived_1._x1, 15)
        self.assertEqual(derived_1._y1, 30)

        transformer = sketchingpy.transform.Transformer()
        transformer.translate(5, 10)

        derived_2 = writable.transform(transformer)
        self.assertEqual(derived_2._x1, 15)
        self.assertEqual(derived_2._y1, 30)

    def test_transformed_clear(self):
        writable = sketchingpy.pillow_struct.TransformedClear('#C0C0C0')
        
        derived_1 = writable.get_with_offset(5, 10)
        self.assertIsNotNone(derived_1)

        transformer = sketchingpy.transform.Transformer()
        transformer.translate(5, 10)

        derived_2 = writable.transform(transformer)
        self.assertIsNotNone(derived_2)
    
    def test_build_rect_with_mode_center(self):
        output = sketchingpy.pillow_struct.build_rect_with_mode(
            7,
            8,
            4,
            4,
            sketchingpy.const.CENTER
        )
        self.assertEqual(output.get_x(), 5)
        self.assertEqual(output.get_y(), 6)
        self.assertEqual(output.get_width(), 4)
        self.assertEqual(output.get_height(), 4)

    def test_build_rect_with_mode_radius(self):
        output = sketchingpy.pillow_struct.build_rect_with_mode(
            7,
            8,
            4,
            4,
            sketchingpy.const.RADIUS
        )
        self.assertEqual(output.get_x(), 3)
        self.assertEqual(output.get_y(), 4)
        self.assertEqual(output.get_width(), 8)
        self.assertEqual(output.get_height(), 8)

    def test_build_rect_with_mode_corner(self):
        output = sketchingpy.pillow_struct.build_rect_with_mode(
            7,
            8,
            4,
            4,
            sketchingpy.const.CORNER
        )
        self.assertEqual(output.get_x(), 7)
        self.assertEqual(output.get_y(), 8)
        self.assertEqual(output.get_width(), 4)
        self.assertEqual(output.get_height(), 4)


    def test_build_rect_with_mode_corners(self):
        output = sketchingpy.pillow_struct.build_rect_with_mode(
            7,
            8,
            7 + 4,
            8 + 4,
            sketchingpy.const.CORNERS
        )
        self.assertEqual(output.get_x(), 7)
        self.assertEqual(output.get_y(), 8)
        self.assertEqual(output.get_width(), 4)
        self.assertEqual(output.get_height(), 4)

    def test_macro(self):
        macro = sketchingpy.pillow_struct.Macro(5, 10)
        self.assertEqual(macro.get_width(), 5)
        self.assertEqual(macro.get_height(), 10)

        writable_1 = sketchingpy.pillow_struct.TransformedWritable(self._example_image, 10, 20)
        writable_2 = sketchingpy.pillow_struct.TransformedLine(10, 20, 30, 40, '#C0C0C0', 1)
        writable_3 = sketchingpy.pillow_struct.TransformedClear('#C0C0C0')

        macro.append(writable_1)
        macro.append(writable_2)
        macro.append(writable_3)

        self.assertEqual(len(macro.get()), 3)

    def test_zero_rect(self):
        rect = sketchingpy.pillow_struct.Rect(1, 2, 4, 8)
        self.assertEqual(rect.get_x(), 1)
        self.assertEqual(rect.get_y(), 2)
        self.assertEqual(rect.get_width(), 4)
        self.assertEqual(rect.get_height(), 8)

        zeroed = sketchingpy.pillow_struct.zero_rect(rect)
        self.assertEqual(zeroed.get_x(), 0)
        self.assertEqual(zeroed.get_y(), 0)
        self.assertEqual(zeroed.get_width(), 4)
        self.assertEqual(zeroed.get_height(), 8)

    def test_get_transformed(self):
        transformer = sketchingpy.transform.Transformer()
        transformer.translate(5, 10)
        transformed = sketchingpy.pillow_struct.get_transformed(
            transformer,
            self._example_image.get_image(),
            20,
            30
        )
        self.assertEqual(transformed.get_x(), 25)
        self.assertEqual(transformed.get_y(), 40)
