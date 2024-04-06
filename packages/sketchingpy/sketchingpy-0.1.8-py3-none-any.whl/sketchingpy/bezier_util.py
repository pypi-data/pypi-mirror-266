"""Utility to build bezier curves.

License:
    BSD
"""
import typing

bezier_available = False

try:
    import bezier  # type: ignore
    import numpy
    bezier_available = True
except:
    pass


class BezierMaker:
    """Wrapper around the bezier library to generate points along a bezier curve."""

    def __init__(self):
        """Create a new curve with no points."""
        if not bezier_available:
            raise RuntimeError('Please pip install bezier to use bezier curves.')

        self._points = []

    def add_point(self, x: float, y: float):
        """Add a point to this curve.

        Add a point to this curve. If it is the first or last point, it is start and destination
        respectively. Otherwise, it is a control point.

        Args:
            x: The x position of the point.
            y: The y position of the point.
        """
        self._points.append((x, y))

    def get_points(self, num_points: int) -> typing.List[typing.Tuple[float, float]]:
        """Get a series of points within the curve.

        Args:
            num_points: The number of points to return.

        Returns:
            List of coordinates along curve.
        """
        if len(self._points) == 0:
            raise RuntimeError('Curve without points.')

        input_array = numpy.transpose(numpy.array(self._points))
        degree = len(self._points) - 1
        curve = bezier.Curve(input_array, degree=degree)

        input_point_ids = range(0, num_points)
        input_fracs = map(lambda x: x / (num_points - 1.0), input_point_ids)
        numpy_points = map(lambda x: curve.evaluate(x), input_fracs)
        simple_points = map(lambda x: (float(x[0]), float(x[1])), numpy_points)
        simple_points_realized = list(simple_points)

        return simple_points_realized
