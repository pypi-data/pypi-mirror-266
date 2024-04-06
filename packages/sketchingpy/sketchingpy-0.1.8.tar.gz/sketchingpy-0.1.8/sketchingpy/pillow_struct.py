"""Structures to support Pillow-based operations.

License:
    BSD
"""

import math
import typing

import PIL.Image
import PIL.ImageDraw

import sketchingpy.abstracted
import sketchingpy.const
import sketchingpy.state_struct
import sketchingpy.transform

COLOR_TUPLE = typing.Union[typing.Tuple[int, int, int], typing.Tuple[int, int, int, int]]


class Rect:
    """Simple structure describing a region in a sketch."""

    def __init__(self, x: float, y: float, width: float, height: float):
        """Create a new region.

        Args:
            x: The x coordinate for the left side of the rectangle.
            y: The y coordinate for the top of the rectangle.
            width: Horizontal size of the rectangle in pixels.
            height: Vertical size of the rectangle in pixels.
        """
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    def get_x(self) -> float:
        """Get the starting x coordinate of this region.

        Returns:
            The x coordinate for the left side of the rectangle.
        """
        return self._x

    def get_y(self) -> float:
        """Get the starting y coordinate of this region.

        Returns:
            The y coordinate for the top of the rectangle.
        """
        return self._y

    def set_x(self, x: float):
        """"Set the starting x coordinate of this region.

        Args:
            x: The x coordinate for the left side of the rectangle.
        """
        self._x = x

    def set_y(self, y: float):
        """Set the starting y coordinate of this region.

        Args:
            y: The y coordinate for the top of the rectangle.
        """
        self._y = y

    def get_width(self) -> float:
        """Get the width of this region.

        Returns:
            Horizontal size of the rectangle in pixels.
        """
        return self._width

    def get_height(self) -> float:
        """Get the height of this region.

        Returns;
            Vertical size of the rectangle in pixels.
        """
        return self._height

    def get_center_x(self) -> float:
        """Get the middle x coordinate of this region.

        Returns:
            Center horizontal coordinate of this region.
        """
        return self.get_x() + self.get_width() / 2

    def get_center_y(self) -> float:
        """Get the middle y coordinate of this region.

        Returns:
            Center vertical coordinate of this region.
        """
        return self.get_y() + self.get_height() / 2

    def set_center_x(self, x: float):
        """Move this region by setting its center horizontal coordinate.

        Args:
            x: The x coordinate that should be the new center of the region.
        """
        new_x = x - self.get_width() / 2
        self.set_x(new_x)

    def set_center_y(self, y: float):
        """Move this region by setting its center vertical coordinate.

        Args:
            y: The y coordinate that should be the new center of the region.
        """
        new_y = y - self.get_height() / 2
        self.set_y(new_y)


class WritableImage:
    """Decorator around a Pillow image which can be written to."""

    def __init__(self, image: PIL.Image.Image, drawable: PIL.ImageDraw.ImageDraw):
        """Create a new writable image record.

        Args:
            image: The Pillow image that isn't writable.
            drawable: The version of image which can be written to.
        """
        self._image = image
        self._drawable = drawable

    def get_image(self) -> PIL.Image.Image:
        """Get the Pillow image.

        Returns:
            The Pillow image that isn't writable.
        """
        return self._image

    def get_drawable(self) -> PIL.ImageDraw.ImageDraw:
        """Get the version of the image which can be written to.

        Returns:
            The version of image which can be written to.
        """
        return self._drawable


class TransformedDrawable:
    """Interface for a transformed drawable component after transformation."""

    def get_with_offset(self, x: float, y: float) -> 'TransformedDrawable':
        """Get a new version of this same object but with a horizontal and vertical offset.

        Args:
            x: The horizontal offset in pixels.
            y: The vertical offset in pixels.

        Returns:
            A copy of this drawable component but with a positional translation applied.
        """
        raise NotImplementedError('Use implementor.')

    def transform(self, transformer: sketchingpy.transform.Transformer) -> 'TransformedDrawable':
        """Get a new version of this same object but with a transformation applied.

        Args:
            transformer: Transformation matrix to apply.

        Returns:
            A copy of this drawable component but with a transformation applied.
        """
        raise NotImplementedError('Use implementor.')

    def draw(self, target: WritableImage):
        """Draw this component.

        Args:
            target: The image on which to draw this component.
        """
        raise NotImplementedError('Use implementor.')


class TransformedWritable(TransformedDrawable):
    """A writable image after transformation."""

    def __init__(self, writable: WritableImage, native_x: float, native_y: float):
        """Create a new record of a writable which is pre-transformed.

        Args:
            writable: The writable after transformation.
            native_x: The horizontal position of where the image should be drawn.
            native_y: The vertical position of where the image should be drawn.
        """
        self._writable = writable
        self._native_x = native_x
        self._native_y = native_y

    def get_writable(self) -> WritableImage:
        """Get the writable image.

        Returns:
            The image which has been pre-transformed.
        """
        return self._writable

    def get_x(self) -> float:
        """Get the intended x coordinate where this image should be drawn.

        Returns:
            The horizontal position of where the image should be drawn.
        """
        return self._native_x

    def get_y(self) -> float:
        """Get the intended y coordinate where this image should be drawn.

        Returns:
            The vertical position of where the image should be drawn.
        """
        return self._native_y

    def get_with_offset(self, x: float, y: float) -> TransformedDrawable:
        return TransformedWritable(self._writable, self._native_x + x, self._native_y + y)

    def transform(self, transformer: sketchingpy.transform.Transformer) -> TransformedDrawable:
        return get_transformed(
            transformer,
            self._writable.get_image(),
            self._native_x,
            self._native_y
        )

    def draw(self, target: WritableImage):
        subject = self._writable.get_image()
        native_pos = (int(self._native_x), int(self._native_y))
        if subject.mode == 'RGB':
            target.get_image().paste(subject, native_pos)
        else:
            target.get_image().paste(subject, native_pos, subject)


class TransformedLine(TransformedDrawable):
    """A pre-transformed simple two point line."""

    def __init__(self, x1: float, y1: float, x2: float, y2: float, stroke: COLOR_TUPLE,
        weight: float):
        """Create a new record of a pre-transformed line.

        Args:
            x1: The first x coordinate.
            y1: The first y coordinate.
            x2: The second x coordinate.
            y2: The second y coordinate.
            stroke: The color with which to draw this line.
            weight: The stroke weight to use when drawing.
        """
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        self._stroke = stroke
        self._weight = weight

    def get_with_offset(self, x: float, y: float) -> TransformedDrawable:
        return TransformedLine(
            self._x1 + x,
            self._y1 + y,
            self._x2 + x,
            self._y2 + y,
            self._stroke,
            self._weight
        )

    def transform(self, transformer: sketchingpy.transform.Transformer) -> TransformedDrawable:
        point_1 = transformer.transform(self._x1, self._y1)
        point_2 = transformer.transform(self._x2, self._y2)
        weight = self._weight * point_1.get_scale()
        return TransformedLine(
            point_1.get_x(),
            point_1.get_y(),
            point_2.get_x(),
            point_2.get_y(),
            self._stroke,
            weight
        )

    def draw(self, target: WritableImage):
        target.get_drawable().line(
            (
                (self._x1, self._y1),
                (self._x2, self._y2)
            ),
            fill=self._stroke,
            width=self._weight
        )


class TransformedClear(TransformedDrawable):
    """A pre-transformed clear operation."""

    def __init__(self, color: COLOR_TUPLE):
        """Create a record of a clear operation.

        Args:
            color: The color with which to clear.
        """
        self._color = color

    def get_with_offset(self, x: float, y: float) -> TransformedDrawable:
        return self

    def transform(self, transformer: sketchingpy.transform.Transformer) -> TransformedDrawable:
        return self

    def draw(self, target: WritableImage):
        image = target.get_image()
        size = image.size
        rect = (0, 0, size[0], size[1])
        target.get_drawable().rectangle(rect, fill=self._color, width=0)


def build_rect_with_mode(x1: float, y1: float, x2: float, y2: float,
    native_mode: int) -> Rect:
    """Build a rect with a mode of coordinate specification.

    Args:
        x1: The left or center x depending on mode.
        y1: The top or center y depending on mode.
        x2: The right or type of width depending on mode.
        y2: The bottom or type of height depending on mode.
        native_mode: The mode with which the coordinates were provided.

    Returns:
        Rect which interprets the given coordinates.
    """
    if native_mode == sketchingpy.const.CENTER:
        start_x = x1 - math.floor(x2 / 2)
        start_y = y1 - math.floor(y2 / 2)
        width = x2
        height = y2
    elif native_mode == sketchingpy.const.RADIUS:
        start_x = x1 - x2
        start_y = y1 - y2
        width = x2 * 2
        height = y2 * 2
    elif native_mode == sketchingpy.const.CORNER:
        start_x = x1
        start_y = y1
        width = x2
        height = y2
    elif native_mode == sketchingpy.const.CORNERS:
        (x1, y1, x2, y2) = sketchingpy.abstracted.reorder_coords(x1, y1, x2, y2)
        start_x = x1
        start_y = y1
        width = x2 - x1
        height = y2 - y1
    else:
        raise RuntimeError('Unknown mode: ' + str(native_mode))

    return Rect(start_x, start_y, width, height)


class Macro:
    """Buffer-like object which keeps track of operations instead of the resulting raster."""

    def __init__(self, width: float, height: float):
        """Build a new macro record.

        Args:
            width: The horizontal size in pixels of the inteded area of drawing.
            height: The vertical size in pixels of the inteded area of drawing.
        """
        self._width = width
        self._height = height
        self._elements: typing.List[TransformedDrawable] = []

    def append(self, target: TransformedDrawable):
        """Add a new drawable to this macro.

        Args:
            target: New element to add to this macro.
        """
        self._elements.append(target)

    def get(self) -> typing.List[TransformedDrawable]:
        """Get the elements in this macro.

        Returns:
            Operations for this macro.
        """
        return self._elements

    def get_width(self) -> float:
        """Get the width of the intended drawing area for this macro.

        Returns:
            Horizontal size of drawing area.
        """
        return self._width

    def get_height(self) -> float:
        """Get the vertical of the intended drawing area for this macro.

        Returns:
            Vertical size of drawing area.
        """
        return self._height


def zero_rect(rect: Rect) -> Rect:
    """Make a copy of a given rect but where the x and y coordinates are set to zero.

    Args:
        rect: The rect to put at 0, 0.

    Returns:
        Copy of the input rect set at 0, 0.
    """
    return Rect(0, 0, rect.get_width(), rect.get_height())


def get_transformed(transformer: sketchingpy.transform.Transformer, surface: PIL.Image.Image,
    x: float, y: float) -> TransformedWritable:
    """Convert an image to a pre-transformed writable.

    Args:
        transformer: The transformation to pre-apply.
        surface: The image on which to apply the transformation.
        x: The intended horizontal draw location of the given position within the given
            transformation.
        y: The intended vertical draw location of the given position within the given
            transformation.

    Returns:
        Writable with the given transformation pre-applied.
    """
    start_rect = Rect(x, y, surface.width, surface.height)

    transformed_center = transformer.transform(
        start_rect.get_center_x(),
        start_rect.get_center_y()
    )

    has_scale = transformed_center.get_scale() != 1
    has_rotation = transformed_center.get_rotation() != 0
    has_content_transform = has_scale or has_rotation
    if has_content_transform:
        angle = transformed_center.get_rotation()
        angle_transform = math.degrees(angle)
        scale = transformed_center.get_scale()
        surface = surface.rotate(angle_transform, expand=True)
        surface = surface.resize((
            int(surface.width * scale),
            int(surface.height * scale)
        ))

    end_rect = Rect(x, y, surface.width, surface.height)
    end_rect.set_center_x(transformed_center.get_x())
    end_rect.set_center_y(transformed_center.get_y())

    return TransformedWritable(
        WritableImage(surface, PIL.ImageDraw.Draw(surface)),
        end_rect.get_x(),
        end_rect.get_y()
    )
