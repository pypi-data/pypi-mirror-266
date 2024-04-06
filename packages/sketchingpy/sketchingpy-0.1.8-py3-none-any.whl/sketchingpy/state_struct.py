"""Data structures describing sketch state including styling and transformation matrix.

License:
    BSD
"""

import sketchingpy.const


class TextAlign:
    """Structure describing text alignment / anchors, possibly using renderer-native values."""

    def __init__(self, horizontal_align, vertical_align):
        """Create a new text alignment structure.

        Args:
            horizontal_align: Description of text horizontal alignment.
            vertical_align: Description of text vertical alignment.
        """
        self._horizontal_align = horizontal_align
        self._vertical_align = vertical_align

    def get_horizontal_align(self):
        """Get the horizontal anchor for text.

        Returns:
            Description of text horizontal alignment which may be renderer-specific.
        """
        return self._horizontal_align

    def get_vertical_align(self):
        """Get the vertical anchor for text.

        Returns:
            Description of text vertical alignment which may be renderer-specific.
        """
        return self._vertical_align


class Font:
    """Structure describing a font using renderer-native values."""

    def __init__(self, identifier, size):
        """Create a record describing a font.

        Args:
            identifier: Name of the font which may be a filename.
            size: The size of the text in px.
        """
        self._identifier = identifier
        self._size = size

    def get_identifier(self):
        """Get the name of this font.

        Returns:
            Name of the font which may be a filename.
        """
        return self._identifier

    def get_size(self):
        """Get the desired size of text.

        Returns:
            The size of the text in px.
        """
        return self._size


class SketchStateMachine:
    """Abstract base class for sketch state."""

    def __init__(self):
        """Create a new state machine."""
        self._fill_enabled = True
        self._fill_str = '#F0F0F0'
        self._stroke_enabled = True
        self._stroke_str = '#333333'
        self._stroke_weight = 1

        self._angle_mode = 'radians'
        self._angle_mode_enum = sketchingpy.const.ANGLE_MODES[self._angle_mode]

        self._arc_mode = 'radius'
        self._arc_mode_enum = sketchingpy.const.SHAPE_MODES[self._arc_mode]

        self._ellipse_mode = 'radius'
        self._ellipse_mode_enum = sketchingpy.const.SHAPE_MODES[self._ellipse_mode]

        self._rect_mode = 'corner'
        self._rect_mode_enum = sketchingpy.const.SHAPE_MODES[self._rect_mode]

        self._text_font = None
        self._text_align = TextAlign('left', 'baseline')
        self._text_align_enum = TextAlign(
            sketchingpy.const.ALIGN_OPTIONS['left'],
            sketchingpy.const.ALIGN_OPTIONS['baseline']
        )

        self._image_mode = 'corner'
        self._image_mode_enum = sketchingpy.const.SHAPE_MODES[self._image_mode]

    ##########
    # Colors #
    ##########

    def set_fill(self, fill: str):
        """Set the fill color.

        Set the color to use for filling shapes and figures.

        Args:
            fill: Name of the color or a hex code.
        """
        self._fill_enabled = True
        self._fill_str = fill

    def get_fill(self) -> str:
        """Get the current fill color.

        Returns:
            Name of the color or a hex code. Undefined if get_fill_enabled() is False.
        """
        return self._fill_str

    def get_fill_native(self):
        """Get the renderer-native version of the fill color.

        Returns:
            Renderer-specific value. Undefined if get_fill_enabled() is False.
        """
        return self._fill_str

    def get_fill_enabled(self) -> bool:
        """Determine if fill is enabled.

        Returns:
            True if fill enabled and false if transparent (drawing outlines).
        """
        return self._fill_enabled

    def clear_fill(self):
        """Indicate that the fill should be transparent / draw outlines."""
        self._fill_enabled = False

    def set_stroke(self, stroke: str):
        """Set the stroke color.

        Set the color to use for drawing outlines for shapes and figures as well as lines.

        Args:
            stroke: Name of the color or a hex code.
        """
        self._stroke_enabled = True
        self._stroke_str = stroke

    def get_stroke(self) -> str:
        """Get the current stroke color.

        Returns:
            Name of the color or a hex code. Undefined if get_stroke_enabled() is False.
        """
        return self._stroke_str

    def get_stroke_native(self):
        """Get the renderer-native version of the stroke color.

        Returns:
            Renderer-specific value. Undefined if get_stroke_enabled() is False.
        """
        return self._stroke_str

    def get_stroke_enabled(self) -> bool:
        """Determine if outline (stroke) should be drawn.

        Returns:
            True if it should be drawn (non-zero stroke weight) and False otherwise.
        """
        return self._stroke_enabled and self._stroke_weight > 0

    def clear_stroke(self):
        """Indicate stroke should not be drawn."""
        self._stroke_enabled = False

    ###########
    # Drawing #
    ###########

    def set_arc_mode(self, mode: str):
        """Specify how Sketchingpy should interpret the position and size arguments for arcs.

        Args:
            mode: String describing the mode to use.
        """
        if mode not in sketchingpy.const.SHAPE_MODES:
            raise RuntimeError('Unknown arc mode: ' + mode)

        self._arc_mode = mode
        self._arc_mode_enum = sketchingpy.const.SHAPE_MODES[self._arc_mode]

    def get_arc_mode(self) -> str:
        """Get mode describing how to interpret arc parameters.

        Returns:
            String describing the mode to use.
        """
        return self._arc_mode

    def get_arc_mode_native(self):
        """Get mode describing how to interpret arc parameters.

        Returns:
            Renderer-specific value.
        """
        return self._arc_mode_enum

    def set_ellipse_mode(self, mode: str):
        """Specify how Sketchingpy should interpret the position and size arguments.

        Args:
            mode: String describing the mode to use.
        """
        if mode not in sketchingpy.const.SHAPE_MODES:
            raise RuntimeError('Unknown ellipse mode: ' + mode)

        self._ellipse_mode = mode
        self._ellipse_mode_enum = sketchingpy.const.SHAPE_MODES[self._ellipse_mode]

    def get_ellipse_mode(self) -> str:
        """Get the mode describing how to interpret parameters for ellipsees.

        Returns:
            String describing the mode to use.
        """
        return self._ellipse_mode

    def get_ellipse_mode_native(self):
        """Get the mode describing how to interpret parameters for ellipses.

        Returns:
            Renderer specific value.
        """
        return self._ellipse_mode_enum

    def set_rect_mode(self, mode: str):
        """Specify how Sketchingpy should interpret the position and size arguments.

        Args:
            mode: String describing the mode to use.
        """
        if mode not in sketchingpy.const.SHAPE_MODES:
            raise RuntimeError('Unknown rect mode: ' + mode)

        self._rect_mode = mode
        self._rect_mode_enum = sketchingpy.const.SHAPE_MODES[self._rect_mode]

    def get_rect_mode(self) -> str:
        """Get the mode describing how to interpret parameters for rectangles.

        Returns:
            String describing the mode to use.
        """
        return self._rect_mode

    def get_rect_mode_native(self):
        """Get the mode describing how to interpret parameters for rectangles.

        Returns:
            Renderer-specific value.
        """
        return self._rect_mode_enum

    def set_stroke_weight(self, stroke_weight: float):
        """Set the stroke size.

        Args:
            stroke_weight: Number of pixels for the stroke weight.
        """
        if stroke_weight < 0:
            raise RuntimeError('Stroke weight must be zero or positive.')

        self._stroke_weight = stroke_weight

    def get_stroke_weight(self) -> float:
        """Get the size of the stroke.

        Returns:
            Number of pixels for the stroke weight.
        """
        if not self._stroke_enabled:
            return 0

        return self._stroke_weight

    def get_stroke_weight_native(self):
        """Get the size of the stroke.

        Returns:
            Renderer-specific value
        """
        return self._stroke_weight

    def set_text_font(self, font: Font):
        """Set the type and size for text drawing.

        Args:
            font: Description of the font and font size to use.
        """
        self._text_font = font

    def get_text_font(self) -> Font:
        """Get the type and size for text drawing.

        Returns:
            Description of the font and font size to use.
        """
        if self._text_font is None:
            raise RuntimeError('Font not yet set.')

        return self._text_font

    def get_text_font_native(self):
        """Get the type and size for text drawing.

        Returns:
            Renderer-specific value.
        """
        return self.get_text_font()

    def set_text_align(self, text_align: TextAlign):
        """Indicate the alignment to use when drawing text.

        Args:
            text_align: Structure describing horizontal and vertical text alignment.
        """
        def check_align(name):
            if name not in sketchingpy.const.ALIGN_OPTIONS:
                raise RuntimeError('Unknown align: %d' % name)

        check_align(text_align.get_horizontal_align())
        check_align(text_align.get_vertical_align())

        self._text_align = text_align
        self._text_align_enum = TextAlign(
            sketchingpy.const.ALIGN_OPTIONS[self._text_align.get_horizontal_align()],
            sketchingpy.const.ALIGN_OPTIONS[self._text_align.get_vertical_align()]
        )

    def get_text_align(self) -> TextAlign:
        """Get the alignment to use when drawing text.

        Returns:
            Structure describing horizontal and vertical text alignment.
        """
        return self._text_align

    def get_text_align_native(self):
        """Get the alignment to use when drawing text.

        Returns:
            Renderer-specific value.
        """
        return self._text_align_enum

    #########
    # Image #
    #########

    def set_image_mode(self, mode: str):
        """Specify how Sketchingpy should place images.

        Args:
            mode: String describing the mode to use.
        """
        if mode not in ['center', 'corner']:
            raise RuntimeError('Unknown image mode: ' + mode)

        self._image_mode = mode
        self._image_mode_enum = sketchingpy.const.SHAPE_MODES[self._image_mode]

    def get_image_mode(self) -> str:
        """Get how Sketchingpy should place images.

        Returns:
            String describing the mode to use.
        """
        return self._image_mode

    def get_image_mode_native(self):
        """Get how Sketchingpy should place images.

        Returns:
            Renderer-specific value.
        """
        return self._image_mode_enum

    ################
    # Other Params #
    ################

    def set_angle_mode(self, mode: str):
        """Indicate how angles should be provided to sketchingpy.

        Args:
            mode: The units (either 'degrees' or 'radians') in which to supply angles.
        """
        if mode not in sketchingpy.const.ANGLE_MODES:
            raise RuntimeError('Unknown angle mode: ' + mode)

        self._angle_mode = mode
        self._angle_mode_enum = sketchingpy.const.ANGLE_MODES[self._angle_mode]

    def get_angle_mode(self) -> str:
        """Get how angles are to be provided to sketchingpy.

        Return:
            The units (either 'degrees' or 'radians') in which angles are to be supplied.
        """
        return self._angle_mode

    def get_angle_mode_native(self):
        """Get how angles are to be provided to sketchingpy.

        Return:
            Renderer-specific value.
        """
        return self._angle_mode_enum
