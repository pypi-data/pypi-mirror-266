import unittest

import sketchingpy.const
import sketchingpy.state_struct


class SketchStateMachineTest(unittest.TestCase):

    def setUp(self):
        self._machine = sketchingpy.state_struct.SketchStateMachine()

    def test_fill(self):
        self._machine.clear_fill()
        self.assertFalse(self._machine.get_fill_enabled())

        self._machine.set_fill('#A0B0C0')
        self.assertEqual(self._machine.get_fill(), '#A0B0C0')
        self.assertTrue(self._machine.get_fill_enabled())

        self._machine.set_fill('#A0B0C0D0')
        self.assertEqual(self._machine.get_fill(), '#A0B0C0D0')
        self.assertTrue(self._machine.get_fill_enabled())

        self._machine.clear_fill()
        self.assertFalse(self._machine.get_fill_enabled())

    def test_stroke(self):
        self._machine.clear_stroke()
        self.assertFalse(self._machine.get_stroke_enabled())

        self._machine.set_stroke('#A0B0C0')
        self.assertEqual(self._machine.get_stroke(), '#A0B0C0')
        self.assertTrue(self._machine.get_stroke_enabled())

        self._machine.set_stroke_weight(0)
        self.assertFalse(self._machine.get_stroke_enabled())

        self._machine.set_stroke_weight(1)
        self.assertTrue(self._machine.get_stroke_enabled())

        self._machine.set_stroke('#A0B0C0D0')
        self.assertEqual(self._machine.get_stroke(), '#A0B0C0D0')
        self.assertTrue(self._machine.get_stroke_enabled())

        self._machine.clear_stroke()
        self.assertFalse(self._machine.get_stroke_enabled())
        self.assertEqual(self._machine.get_stroke_weight(), 0)

        self._machine.set_stroke('#A0B0C0')
        self.assertTrue(self._machine.get_stroke_enabled())
        self.assertEqual(self._machine.get_stroke_weight(), 1)

    def test_arc_mode(self):
        self._machine.set_arc_mode('center')
        self.assertEqual(self._machine.get_arc_mode(), 'center')

        self._machine.set_arc_mode('radius')
        self.assertEqual(self._machine.get_arc_mode(), 'radius')

    def test_ellipse_mode(self):
        self._machine.set_ellipse_mode('center')
        self.assertEqual(self._machine.get_ellipse_mode(), 'center')

        self._machine.set_ellipse_mode('radius')
        self.assertEqual(self._machine.get_ellipse_mode(), 'radius')

    def test_rect_mode(self):
        self._machine.set_rect_mode('center')
        self.assertEqual(self._machine.get_rect_mode(), 'center')

        self._machine.set_rect_mode('radius')
        self.assertEqual(self._machine.get_rect_mode(), 'radius')

    def test_stroke_weight(self):
        self._machine.set_stroke_weight(1)
        self.assertEqual(self._machine.get_stroke_weight(), 1)
        self.assertTrue(self._machine.get_stroke_enabled())

        self._machine.clear_stroke()
        self.assertEqual(self._machine.get_stroke_weight(), 0)
        self.assertFalse(self._machine.get_stroke_enabled())

        self._machine.set_stroke_weight(2)
        self.assertEqual(self._machine.get_stroke_weight(), 0)
        self.assertFalse(self._machine.get_stroke_enabled())

        self._machine.set_stroke('#A0B0C0')
        self.assertEqual(self._machine.get_stroke_weight(), 2)
        self.assertTrue(self._machine.get_stroke_enabled())

        self._machine.set_stroke_weight(0)
        self.assertEqual(self._machine.get_stroke_weight(), 0)
        self.assertFalse(self._machine.get_stroke_enabled())

    def test_stroke_maintained(self):
        self._machine.set_stroke_weight(1)
        self._machine.set_stroke('#A0B0C0')

        self.assertEqual(self._machine.get_stroke_weight(), 1)
        self.assertTrue(self._machine.get_stroke_enabled())
        self.assertEqual(self._machine.get_stroke(), '#A0B0C0')

        self._machine.set_stroke_weight(0)
        self.assertEqual(self._machine.get_stroke_weight(), 0)
        self.assertFalse(self._machine.get_stroke_enabled())
        self.assertEqual(self._machine.get_stroke(), '#A0B0C0')

        self._machine.set_stroke_weight(2)
        self.assertEqual(self._machine.get_stroke_weight(), 2)
        self.assertTrue(self._machine.get_stroke_enabled())
        self.assertEqual(self._machine.get_stroke(), '#A0B0C0')

    def test_text_font(self):
        self._machine.set_text_font('a')
        self.assertEqual(self._machine.get_text_font(), 'a')

        self._machine.set_text_font('b')
        self.assertEqual(self._machine.get_text_font(), 'b')

    def test_text_align(self):
        self._machine.set_text_align(sketchingpy.state_struct.TextAlign(
            'right',
            'baseline'
        ))
        self.assertEqual(
            self._machine.get_text_align().get_horizontal_align(),
            'right'
        )
        self.assertEqual(
            self._machine.get_text_align().get_vertical_align(),
            'baseline'
        )

        self._machine.set_text_align(sketchingpy.state_struct.TextAlign(
            'center',
            'top'
        ))
        self.assertEqual(
            self._machine.get_text_align().get_horizontal_align(),
            'center'
        )
        self.assertEqual(
            self._machine.get_text_align().get_vertical_align(),
            'top'
        )

    def test_image_mode(self):
        self._machine.set_image_mode('center')
        self.assertEqual(self._machine.get_image_mode(), 'center')

        self._machine.set_image_mode('corner')
        self.assertEqual(self._machine.get_image_mode(), 'corner')

    def test_angle_mode(self):
        self._machine.set_angle_mode('radians')
        self.assertEqual(self._machine.get_angle_mode(), 'radians')

        self._machine.set_angle_mode('degrees')
        self.assertEqual(self._machine.get_angle_mode(), 'degrees')
