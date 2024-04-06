"""Data structures describing shapes.

License:
    BSD
"""

import typing


class Line:
    """Data structure describing a segment.

    Data structure describing a segment which can be a straight line but also a curve like a bezier
    curve.
    """

    def get_destination_x(self) -> float:
        """Get the ending horizontal coordinate of this segment.

        Returns:
            The x coordinate that this segment ends on.
        """
        raise NotImplementedError('Use implementor.')

    def get_destination_y(self) -> float:
        """Get the ending vertical coordinate of this segment.

        Returns:
            The y coordinate that this segment ends on.
        """
        raise NotImplementedError('Use implementor.')

    def get_min_x(self) -> float:
        """Get the minimum of the x coordinates in this segment.

        Returns:
            Minimum x coordinate of this segment.
        """
        raise NotImplementedError('Use impelentor.')

    def get_max_x(self) -> float:
        """Get the maximum of the x coordinates in this segment.

        Returns:
            Maximum x coordinate of this segment.
        """
        raise NotImplementedError('Use impelentor.')

    def get_min_y(self) -> float:
        """Get the minimum of the y coordinates in this segment.

        Returns:
            Minimum y coordinate of this segment.
        """
        raise NotImplementedError('Use impelentor.')

    def get_max_y(self) -> float:
        """Get the maximum of the y coordinates in this segment.

        Returns:
            Maximum y coordinate of this segment.
        """
        raise NotImplementedError('Use impelentor.')

    def get_strategy(self) -> str:
        """Get the type of line that this segment represents.

        Returns:
            Line strategy like "straight" or "bezier" as a string.
        """
        raise NotImplementedError('Use implementor.')

    def get_control_x1(self):
        """Get the horizontal coordinate of the first control point.

        Returns:
            The x coordinate of the first control point.
        """
        raise NotImplementedError('Not supported by strategy.')

    def get_control_y1(self):
        """Get the vertical coordinate of the first control point.

        Returns:
            The y coordinate of the first control point.
        """
        raise NotImplementedError('Not supported by strategy.')

    def get_control_x2(self):
        """Get the horizontal coordinate of the second control point.

        Returns:
            The x coordinate of the second control point.
        """
        raise NotImplementedError('Not supported by strategy.')

    def get_control_y2(self):
        """Get the vertical coordinate of the second control point.

        Returns:
            The y coordinate of the second control point.
        """
        raise NotImplementedError('Not supported by strategy.')


class StraightLine(Line):
    """A segment which is a straight line between two points."""

    def __init__(self, destination_x: float, destination_y: float):
        """Create a new straight line segmenet.

        Args:
            destination_x: The vertical location of the end coordinate.
            destination_y: The horizontal location of the end coordinate.
        """
        self._destination_x = destination_x
        self._destination_y = destination_y

    def get_destination_x(self) -> float:
        return self._destination_x

    def get_destination_y(self) -> float:
        return self._destination_y

    def get_min_x(self) -> float:
        return self._destination_x

    def get_max_x(self) -> float:
        return self._destination_x

    def get_min_y(self) -> float:
        return self._destination_y

    def get_max_y(self) -> float:
        return self._destination_y

    def get_strategy(self) -> str:
        return 'straight'


class BezierLine(Line):
    """A segment which is a bezier curve between two points."""

    def __init__(self, control_x1: float, control_y1: float, control_x2: float, control_y2: float,
        destination_x: float, destination_y: float):
        """Create a new bezier curve.

        Args:
            control_x1: The horizontal location of the first control point.
            control_y1: The vertical location of the first control point.
            control_x2: The horizontal location of the second control point.
            control_y2: The vertical location of the second control point.
            destination_x: The vertical location of the end coordinate.
            destination_y: The horizontal location of the end coordinate.
        """
        self._control_x1 = control_x1
        self._control_y1 = control_y1
        self._control_x2 = control_x2
        self._control_y2 = control_y2
        self._destination_x = destination_x
        self._destination_y = destination_y

    def get_control_x1(self):
        return self._control_x1

    def get_control_y1(self):
        return self._control_y1

    def get_control_x2(self):
        return self._control_x2

    def get_control_y2(self):
        return self._control_y2

    def get_destination_x(self):
        return self._destination_x

    def get_destination_y(self):
        return self._destination_y

    def get_min_x(self) -> float:
        return min([
            self._control_x1,
            self._control_x2,
            self._destination_x
        ])

    def get_max_x(self) -> float:
        return max([
            self._control_x1,
            self._control_x2,
            self._destination_x
        ])

    def get_min_y(self) -> float:
        return min([
            self._control_y1,
            self._control_y2,
            self._destination_y
        ])

    def get_max_y(self) -> float:
        return max([
            self._control_y1,
            self._control_y2,
            self._destination_y
        ])

    def get_strategy(self) -> str:
        return 'bezier'


class Shape:
    """Structure describing a multi-segement shape."""

    def __init__(self, start_x: float, start_y: float):
        """Create a new multi-segment shape.

        Args:
            start_x: The starting x position of the shape.
            start_y: The starting y position of the shape.
        """
        self._start_x = start_x
        self._start_y = start_y
        self._closed = False
        self._finished = False
        self._segments: typing.List[Line] = []

    def add_line_to(self, x: float, y: float):
        """Add a straight line to a shape.

        Draw a straight line from the current position to a new destination which is used as the
        next "current" position.

        Args:
            x: The x coordinate to which the line should be drawn.
            y: The y coordinate to which the line should be drawn.
        """
        self._assert_not_finished()
        self._segments.append(StraightLine(x, y))

    def add_bezier_to(self, control_x1: float, control_y1: float, control_x2: float,
        control_y2: float, destination_x: float, destination_y: float):
        """Add a bezier curve to a shape.

        Draw a bezier curve from the current position to a new destination which is used as the next
        "current" position.

        Args:
            control_x1: The horizontal location of the first control point.
            control_y1: The vertical location of the first control point.
            control_x2: The horizontal location of the second control point.
            control_y2: The vertical location of the second control point.
            destination_x: The vertical location of the end coordinate.
            destination_y: The horizontal location of the end coordinate.
        """
        self._assert_not_finished()
        self._segments.append(BezierLine(
            control_x1,
            control_y1,
            control_x2,
            control_y2,
            destination_x,
            destination_y
        ))

    def get_start_x(self) -> float:
        """Retrieve the first x coordinate of this shape.

        Get the horizontal coordinate from which the first segment draws.

        Returns:
            The starting x coordinate.
        """
        return self._start_x

    def get_start_y(self) -> float:
        """Retrieve the first y coordinate of this shape.

        Get the vertical coordinate from which the first segment draws.

        Returns:
            The starting y coordinate.
        """
        return self._start_y

    def get_segments(self) -> typing.Iterable[Line]:
        """Retrieve shape segments.

        Retrieve objects describing each of the segments in a shape.

        Returns:
            Segements in this shape.
        """
        return self._segments

    def get_is_finished(self) -> bool:
        """Determine if a shape is finished.

        Determine if the shape is finished so can be drawn. Returns true if finished (can be drawn)
        and false otherwise (still building). A shape cannot be drawn until it is finished which can
        be accomplished by either calling end or close.

        Returns:
            True if finished and false otherwise.
        """
        return self._finished

    def end(self):
        """Draw a shape.

        Draw a shape which consists of multiple line or curve segments and which can be either open
        (stroke only) or closed (can be filled).
        """
        self._assert_not_finished()
        self._finished = True
        self._closed = False

    def close(self):
        """Add a straight line to the starting coordinate.

        Add a line in the shape from the current position to the start position, marking the shape
        as finished and closed which allows it to be filled.
        """
        self._assert_not_finished()
        self._finished = True
        self._closed = True

    def get_is_closed(self) -> bool:
        """Determine if a shape can be filled.

        Determine if the shape is closed so can be filled. Returns true if closed (can be filled)
        and false otherwise.

        Returns:
            True if closed and false otherwise.
        """
        self._assert_finished()
        return self._closed

    def get_min_x(self):
        """Determine the minimum x coordinate of a shape.

        Determine the minimum x coordinate (relative to start position) that this shape may reach
        to. This includes bezier control points but does not try to include stroke weight in its
        calculation.

        Returns:
            Minimum x coordinate.
        """
        self._assert_finished()
        return min([self._start_x] + [x.get_min_x() for x in self._segments])

    def get_max_x(self):
        """Determine the maximum x coordinate of a shape.

        Determine the maximum x coordinate (relative to start position) that this shape may reach
        to. This includes bezier control points but does not try to include stroke weight in its
        calculation.

        Returns:
            Maximum x coordinate.
        """
        self._assert_finished()
        return max([self._start_x] + [x.get_max_x() for x in self._segments])

    def get_min_y(self):
        """Determine the minimum y coordinate of a shape.

        Determine the minimum y coordinate (relative to start position) that this shape may reach
        to. This includes bezier control points but does not try to include stroke weight in its
        calculation.

        Returns:
            Minimum y coordinate.
        """
        self._assert_finished()
        return min([self._start_y] + [x.get_min_y() for x in self._segments])

    def get_max_y(self):
        """Determine the maximum y coordinate of a shape.

        Determine the maximum y coordinate (relative to start position) that this shape may reach
        to. This includes bezier control points but does not try to include stroke weight in its
        calculation.

        Returns:
            Maximum y coordinate.
        """
        self._assert_finished()
        return max([self._start_y] + [x.get_max_y() for x in self._segments])

    def _assert_not_finished(self):
        if self._finished:
            raise RuntimeError('Whoops! This shape is already finished.')

    def _assert_finished(self):
        if not self._finished:
            raise RuntimeError('Whoops! This shape is not yet finished.')
