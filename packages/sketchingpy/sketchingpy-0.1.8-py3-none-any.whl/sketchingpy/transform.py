"""Data structures providing transformation matrix functionality if native logic is not available.

Data structures providing Python-based transformation matrix functionality if native logic is not
available in the underlying renderer.

License:
    BSD
"""

import math
import typing

has_numpy = False
try:
    import numpy
    has_numpy = True
except:
    pass


class TransformedPoint:
    """A point which has gone through zero or more transformations."""

    def __init__(self, x: float, y: float, scale: float, rotation: float):
        """Create a new transformed point.

        Args:
            x: Horizontal coordinate for this point after transformation.
            y: Vertical coordinate for this point after transformation.
            scale: The overall scale factor applied to this point.
            rotation: The overall rotation applied to this point.
        """
        self._x = x
        self._y = y
        self._scale = scale
        self._rotation = rotation

    def get_x(self) -> float:
        """Get the post-transformation x coordinate.

        Returns:
            Horizontal coordinate for this point after transformation.
        """
        return self._x

    def get_y(self) -> float:
        """Get the post-transformation y coordinate.

        Returns:
            Vertical coordinate for this point after transformation.
        """
        return self._y

    def get_scale(self) -> float:
        """Get the overall scale reflected in this point.

        Returns:
            The overall scale factor applied to this point.
        """
        return self._scale

    def get_rotation(self) -> float:
        """Get the overall rotation reflected in this point.

        Returns:
            The overall rotation factor applied to this point.
        """
        return self._rotation


class Transformer:
    """Utility to transform points."""

    def __init__(self, matrix: typing.Optional['numpy.ndarray'] = None, scale: float = 1,
        rotation: float = 0):
        """Create a new transformer.

        Args:
            matrix: Starting transformation matrix.
            scale: Starting overall scale.
            rotation: Starting overall rotation.
        """

        if not has_numpy:
            raise RuntimeError('Need numpy in order to use transformer on this renderer.')

        matrix_unset = matrix is None
        scale_unset = abs(scale - 1) < 0.00001
        rotation_unset = abs(rotation - 0) < 0.00001

        self._is_default = matrix_unset and scale_unset and rotation_unset
        self._matrix = numpy.identity(3) if matrix is None else matrix
        self._scale = scale
        self._rotation = rotation

    def translate(self, x: float, y: float):
        """Apply a translation to the current transformation matrix.

        Args:
            x: By how much to offset the horizontal coordinate.
            y: By how much to offset the vertical coordinate.
        """
        transformation = numpy.identity(3)
        transformation[0][2] = x
        transformation[1][2] = y
        self._matrix = numpy.dot(self._matrix, transformation)
        self._is_default = False

    def scale(self, scale: float):
        """Apply a scale to the current transformation matrix.

        Args:
            scale: The scale to apply.
        """
        transformation = numpy.identity(3)
        transformation[0][0] = scale
        transformation[1][1] = scale
        self._matrix = numpy.dot(self._matrix, transformation)
        self._scale *= scale
        self._is_default = False

    def rotate(self, angle: float):
        """Apply a rotation to the current transforation matrix counter-clockwise.

        Args:
            angle: The angle of rotation to apply as radians.
        """
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        transformation = numpy.identity(3)
        transformation[0][0] = cos_angle
        transformation[1][1] = cos_angle
        transformation[1][0] = -1 * sin_angle
        transformation[0][1] = sin_angle

        self._matrix = numpy.dot(self._matrix, transformation)
        self._rotation += angle
        self._is_default = False

    def transform(self, x: float, y: float) -> TransformedPoint:
        """Transform a point.

        Args:
            x: The horizontal coordinate to be transformed.
            y: The vertical coordinate to be transformed.

        Returns:
            Point after transformation.
        """
        if self._is_default:
            return TransformedPoint(x, y, self._scale, self._rotation)

        input_array = numpy.array([x, y, 1])
        output = numpy.dot(self._matrix, input_array)

        x = output[0]
        y = output[1]

        return TransformedPoint(x, y, self._scale, self._rotation)

    def quick_copy(self) -> 'Transformer':
        """Create a shallow copy of this transformer.

        Returns:
            Transformer which has the same transform matrix as this original transformer.
        """
        return Transformer(self._matrix, self._scale, self._rotation)
