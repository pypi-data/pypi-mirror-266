import unittest

import pygame.locals

import sketchingpy.const
import sketchingpy.sketch2d_keymap


class Sketch2DKeymapTest(unittest.TestCase):

    def test_managed(self):
        self.assertEqual(
            sketchingpy.sketch2d_keymap.KEY_MAP[pygame.locals.K_UP],
            sketchingpy.const.KEYBOARD_UP_BUTTON
        )

    def test_unmanaged(self):
        self.assertEqual(
            sketchingpy.sketch2d_keymap.KEY_MAP[pygame.locals.K_COLON],
            'colon'
        )

    def test_normal(self):
        self.assertEqual(
            sketchingpy.sketch2d_keymap.KEY_MAP[pygame.locals.K_a],
            'a'
        )
