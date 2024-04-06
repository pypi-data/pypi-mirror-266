"""Convienence functions for Pillow (PIL).

License:
    BSD
"""

import itertools
import math
import typing

import PIL.Image
import PIL.ImageColor
import PIL.ImageDraw

import sketchingpy.bezier_util
import sketchingpy.shape_struct
import sketchingpy.state_struct

COLOR_MAYBE = typing.Optional[typing.Union[
    typing.Tuple[int, int, int],
    typing.Tuple[int, int, int, int]
]]


class PillowUtilImage:
    """Wrapper around a native Pillow image with additional metadata."""

    def __init__(self, x: float, y: float, width: float, height: float, image: PIL.Image.Image):
        """Create a new wrapped pillow image.

        Args:
            x: The starting x coordinate of this image in pixels.
            y: The starting y coordinate of this image in pixels.
            width: The current width of this image in pixels.
            height: The current height of this image in pixels.
            image: The image decorated.
        """
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._image = image

    def get_x(self) -> float:
        """Get the horizontal coordinate of this image (left).

        Returns:
            The starting x coordinate of this image in pixels.
        """
        return self._x

    def get_y(self) -> float:
        """Get the vertical coordinate of this image (top).

        Returns:
            The starting y coordinate of this image in pixels.
        """
        return self._y

    def get_width(self) -> float:
        """Get the horizontal size of this image at time of construction.

        Returns:
            Width of this image in pixels.
        """
        return self._width

    def get_height(self) -> float:
        """Get the vertical size of this image at time of construction.

        Returns:
            Height of this image in pixels.
        """
        return self._height

    def get_image(self) -> PIL.Image.Image:
        """Get the underlying Pillow image.

        Returns:
            The pillow image that this wraps.
        """
        return self._image


def make_arc_image(min_x: float, min_y: float, width: float, height: float, start_rad: float,
    end_rad: float, stroke_enabled: bool, fill_enabled: bool, stroke_color: COLOR_MAYBE,
    fill_color: COLOR_MAYBE, stroke_weight: float) -> PillowUtilImage:
    """Draw an arc using Pillow.

    Args:
        min_x: The left coordinate.
        min_y: The top coordinate.
        width: Width of the arc in pixels.
        height: Height of the arc in pixels.
        start_rad: Starting angle (radians) of the arc.
        end_rad: Ending angle (radians) of the arc.
        stroke_enabled: Boolean indicating if the stroke should be drawn.
        fill_enabled: Boolean indicating if the fill should be drawn.
        stroke_color: The color as tuple with which the stroke should be drawn or None if no stroke.
        fill_color: The color as tuple with which the fill should be drawn or None if no fill.
        stroke_weight: The size of the stroke in pixels.

    Returns:
        Decorated Pillow image with the drawn arc.
    """
    if stroke_enabled:
        stroke_weight_realized = stroke_weight
    else:
        stroke_weight_realized = 0

    width_offset = width + stroke_weight_realized
    height_offset = height + stroke_weight_realized

    size = (round(width_offset) + 1, round(height_offset) + 1)
    target_image = PIL.Image.new('RGBA', size, (255, 255, 255, 0))
    target_surface = PIL.ImageDraw.Draw(target_image, 'RGBA')

    bounds = (
        (0, 0),
        (width, height)
    )

    start_deg = math.degrees(start_rad) - 90
    end_deg = math.degrees(end_rad) - 90

    if fill_enabled and fill_color is not None:
        target_surface.chord(
            bounds,
            start_deg,
            end_deg,
            fill=fill_color
        )

    if stroke_enabled and stroke_color is not None:
        target_surface.arc(
            bounds,
            start_deg,
            end_deg,
            fill=stroke_color,
            width=stroke_weight_realized
        )

    return PillowUtilImage(
        min_x,
        min_y,
        width_offset,
        height_offset,
        target_image
    )


def make_rect_image(min_x: float, min_y: float, width: float, height: float, stroke_enabled: bool,
    fill_enabled: bool, stroke_color: COLOR_MAYBE, fill_color: COLOR_MAYBE,
    stroke_weight: float) -> PillowUtilImage:
    """Draw a rectangle using Pillow.

    Args:
        min_x: The left coordinate.
        min_y: The top coordinate.
        width: Width of the rect in pixels.
        height: Height of the rect in pixels.
        stroke_enabled: Boolean indicating if the stroke should be drawn.
        fill_enabled: Boolean indicating if the fill should be drawn.
        stroke_color: The color as tuple with which the stroke should be drawn or None if no stroke.
        fill_color: The color as tuple with which the fill should be drawn or None if no fill.
        stroke_weight: The size of the stroke in pixels.

    Returns:
        Decorated Pillow image with the drawn rect.
    """
    if stroke_enabled:
        stroke_weight_realized = stroke_weight
    else:
        stroke_weight_realized = 0

    width_offset = width + math.floor(stroke_weight_realized / 2) * 2
    height_offset = height + math.floor(stroke_weight_realized / 2) * 2

    size = (round(width_offset) + 1, round(height_offset) + 1)
    target_image = PIL.Image.new('RGBA', size, (255, 255, 255, 0))
    target_surface = PIL.ImageDraw.Draw(target_image, 'RGBA')

    bounds = (
        0,
        0,
        width_offset,
        height_offset
    )
    target_surface.rectangle(
        bounds,
        fill=fill_color if fill_enabled else None,
        outline=stroke_color if stroke_enabled else None,
        width=stroke_weight_realized
    )

    return PillowUtilImage(
        min_x - round(stroke_weight_realized / 2),
        min_y - round(stroke_weight_realized / 2),
        width_offset,
        height_offset,
        target_image
    )


def make_ellipse_image(min_x: float, min_y: float, width: float, height: float,
    stroke_enabled: bool, fill_enabled: bool, stroke_color: COLOR_MAYBE, fill_color: COLOR_MAYBE,
    stroke_weight: float) -> PillowUtilImage:
    """Draw a ellipse using Pillow.

    Args:
        min_x: The left coordinate.
        min_y: The top coordinate.
        width: Width of the rect in pixels.
        height: Height of the rect in pixels.
        stroke_enabled: Boolean indicating if the stroke should be drawn.
        fill_enabled: Boolean indicating if the fill should be drawn.
        stroke_color: The color as tuple with which the stroke should be drawn or None if no stroke.
        fill_color: The color as tuple with which the fill should be drawn or None if no fill.
        stroke_weight: The size of the stroke in pixels.

    Returns:
        Decorated Pillow image with the drawn ellipse.
    """
    if stroke_enabled:
        stroke_weight_realized = stroke_weight
    else:
        stroke_weight_realized = 0

    width_offset = width + math.floor(stroke_weight_realized / 2) * 2
    height_offset = height + math.floor(stroke_weight_realized / 2) * 2

    size = (round(width_offset) + 1, round(height_offset) + 1)
    target_image = PIL.Image.new('RGBA', size, (255, 255, 255, 0))
    target_surface = PIL.ImageDraw.Draw(target_image, 'RGBA')

    bounds = (
        0,
        0,
        width_offset,
        height_offset
    )
    target_surface.ellipse(
        bounds,
        fill=fill_color if fill_enabled else None,
        outline=stroke_color if stroke_enabled else None,
        width=stroke_weight_realized
    )

    return PillowUtilImage(
        min_x - round(stroke_weight_realized / 2),
        min_y - round(stroke_weight_realized / 2),
        width_offset,
        height_offset,
        target_image
    )


class SegmentSimplifier:
    """Utility to help draw shapes' segments in Pillow."""

    def __init__(self, start_x: float, start_y: float):
        """Create a new simplifier.

        Args:
            start_x: The starting x coordinate of the shape.
            start_y: The starting y coordinate of the shape.
        """
        self._previous_x = start_x
        self._previous_y = start_y

    def simplify(self,
        segment: sketchingpy.shape_struct.Line) -> typing.Iterable[typing.Iterable[float]]:
        """Turn a segment into a series of coordinates.

        Simplify a segment into a simple series of x, y coordinates which approximate the underlying
        shape using a series of straight lines.

        Args:
            segment: The segment to simplify.

        Returns:
            Collection of x, y coordinates.
        """
        ret_vals: typing.Iterable[typing.Tuple[float, float]] = []

        strategy = segment.get_strategy()
        if strategy == 'straight':
            ret_vals = ((segment.get_destination_x(), segment.get_destination_y()),)
        elif strategy == 'bezier':
            change_y = abs(segment.get_control_y2() - segment.get_control_y1())
            change_x = abs(segment.get_control_x2() - segment.get_control_x1())

            num_segs = (change_y**2 + change_x**2) ** 0.5 / 10
            num_segs_int = int(num_segs)

            bezier_maker = sketchingpy.bezier_util.BezierMaker()
            bezier_maker.add_point(self._previous_x, self._previous_y)
            bezier_maker.add_point(segment.get_control_x1(), segment.get_control_y1())
            bezier_maker.add_point(segment.get_control_x2(), segment.get_control_y2())
            bezier_maker.add_point(segment.get_destination_x(), segment.get_destination_y())

            ret_vals = bezier_maker.get_points(num_segs_int)
        else:
            raise RuntimeError('Unknown segment strategy: ' + strategy)

        self._previous_x = segment.get_destination_x()
        self._previous_y = segment.get_destination_y()

        return ret_vals


def make_shape_image(shape: sketchingpy.shape_struct.Shape, stroke_enabled: bool,
    fill_enabled: bool, stroke_color: COLOR_MAYBE, fill_color: COLOR_MAYBE,
    stroke_weight: float) -> PillowUtilImage:
    """Draw a Sketchingpy shape into a pillow image.

    Args:
        shape: The shape to be drawn.
        stroke_enabled: Boolean indicating if the stroke should be drawn.
        fill_enabled: Boolean indicating if the fill should be drawn.
        stroke_color: The color as tuple with which the stroke should be drawn or None if no stroke.
        fill_color: The color as tuple with which the fill should be drawn or None if no fill.
        stroke_weight: The size of the stroke in pixels.

    Returns:
        Decorated Pillow image with the drawn shape.
    """

    if not shape.get_is_finished():
        raise RuntimeError('Finish shape before drawing.')

    min_x = shape.get_min_x()
    max_x = shape.get_max_x()
    min_y = shape.get_min_y()
    max_y = shape.get_max_y()

    width = max_x - min_x
    height = max_y - min_y
    width_offset = width + stroke_weight * 2
    height_offset = height + stroke_weight * 2

    size = (round(width_offset) + 1, round(height_offset) + 1)
    target_image = PIL.Image.new('RGBA', size, (255, 255, 255, 0))
    target_surface = PIL.ImageDraw.Draw(target_image, 'RGBA')

    def adjust_coord(coord):
        return (
            coord[0] - min_x + stroke_weight,
            coord[1] - min_y + stroke_weight
        )

    start_x = shape.get_start_x()
    start_y = shape.get_start_y()
    start_coords = [(start_x, start_y)]

    simplified_segements = []
    simplifier = SegmentSimplifier(start_x, start_y)
    for segment in shape.get_segments():
        simplified_segements.append(simplifier.simplify(segment))

    later_coords = itertools.chain(*simplified_segements)
    all_coords = itertools.chain(start_coords, later_coords)
    coords = [adjust_coord(x) for x in all_coords]

    if shape.get_is_closed():
        target_surface.polygon(coords, fill=fill_color, outline=stroke_color, width=stroke_weight)
    else:
        target_surface.line(coords, fill=stroke_color, width=stroke_weight, joint='curve')

    return PillowUtilImage(
        min_x - stroke_weight,
        min_y - stroke_weight,
        width_offset,
        height_offset,
        target_image
    )


def make_text_image(x: float, y: float, content: str, font: PIL.ImageFont.ImageFont,
    stroke_enabled: bool, fill_enabled: bool, stroke: COLOR_MAYBE, fill: COLOR_MAYBE,
    stroke_weight: float, anchor: str):
    """Draw text into a pillow image.

    Args:
        x: The x coordinate of the anchor.
        y: The y coordinate of the anchor.
        font: The font (PIL native) to use in drawing the text.
        stroke_enabled: Boolean indicating if the stroke should be drawn.
        fill_enabled: Boolean indicating if the fill should be drawn.
        stroke: The color as tuple with which the stroke should be drawn or None if no stroke.
        fill: The color as tuple with which the fill should be drawn or None if no fill.
        stroke_weight: The size of the stroke in pixels.
        anchor: Anchor string describing vertical and horizontal alignment.

    Returns:
        Decorated Pillow image with the drawn text.
    """

    temp_image = PIL.Image.new('RGBA', (1, 1), (255, 255, 255, 0))
    temp_surface = PIL.ImageDraw.Draw(temp_image, 'RGBA')
    stroke_weight_int = round(stroke_weight)
    bounding_box = temp_surface.textbbox(
        (stroke_weight_int, stroke_weight_int),
        content,
        font=font,
        anchor=anchor,
        stroke_width=stroke_weight_int
    )

    start_x = bounding_box[0]
    end_x = bounding_box[2]

    start_y = bounding_box[1]
    end_y = bounding_box[3]

    width = end_x - start_x
    height = end_y - start_y

    width_offset = width + stroke_weight * 2
    height_offset = height + stroke_weight * 2

    size = (round(width_offset) + 1, round(height_offset) + 1)
    target_image = PIL.Image.new('RGBA', size, (255, 255, 255, 0))
    target_surface = PIL.ImageDraw.Draw(target_image, 'RGBA')

    if stroke_enabled:
        target_surface.text(
            (
                round(-1 * start_x + stroke_weight),
                round(-1 * start_y + stroke_weight)
            ),
            content,
            font=font,
            anchor=anchor,
            stroke_width=round(stroke_weight),
            stroke_fill=stroke,
            fill=(0, 0, 0, 0)
        )

    if fill_enabled:
        target_surface.text(
            (-1 * start_x + stroke_weight, -1 * start_y + stroke_weight),
            content,
            font=font,
            anchor=anchor,
            fill=fill
        )

    return PillowUtilImage(
        start_x - stroke_weight + x,
        start_y - stroke_weight + y,
        width_offset,
        height_offset,
        target_image
    )
