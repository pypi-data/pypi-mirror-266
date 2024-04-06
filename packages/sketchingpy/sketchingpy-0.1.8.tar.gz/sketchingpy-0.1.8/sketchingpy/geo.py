"""Utilities for geospatial operations.

Utilities for geospatial operations, inspired by processing-geopoint under the BSD license at
https://github.com/SchmidtDSE/processing-geopoint/tree/main.

License:
    BSD
"""
import itertools
import math
import typing

import sketchingpy.shape_struct

BASE_SCALE = 0.0001
BASE_LATITUDE = 0
BASE_LONGITUDE = 0
BASE_X = 0
BASE_Y = 0

RADIUS_MAJOR = 6378137.0
RADIUS_MINOR = 6356752.3142

TRANSFORM_MAYBE = typing.Optional['GeoTransformation']


class PixelOffset:
    """Structure to place a map projection into pixel space."""

    def __init__(self, x: float, y: float):
        """Create PixelOffset.

        Make data structure indicating where the map should be centered inside of a sketch in terms
        of pixels.

        Args:
            x: Horizontal coordinate at which to center in pixels.
            y: Vertical coordinate at which to center in pixels.
        """
        self._x = x
        self._y = y

    def get_x(self) -> float:
        """Get the x center position.

        Returns:
            Horizontal coordinate at which to center in pixels.
        """
        return self._x

    def get_y(self) -> float:
        """Get the y center position.

        Returns:
            Vertical coordinate at which to center in pixels.
        """
        return self._y


class GeoPoint:
    """Utility to convert latitude and longitud to x and y."""

    def __init__(self, longitude: float, latitude: float):
        """Create a new geographic point.

        Create utility to convert latitude and longitude points to pixel coordinates (x and y) using
        a Web Mercador projection.

        Args:
            longitude: The longitude of the point in degrees.
            latitude: The latitude of the point in degrees.
        """
        self._longitude = longitude
        self._latitude = latitude
        self._x = self._longitude_to_x(self._longitude)
        self._y = self._latitude_to_y(self._latitude)

    def get_x(self, transform: TRANSFORM_MAYBE = None) -> float:
        """Get the horizontal pixel coordinate for this geographic point.

        Args:
            transform: Map view (transformation) to use in finding this coordinate.

        Returns:
            Converted x position in pixels.
        """
        if transform is None:
            return self._x * BASE_SCALE

        geo_offset_x = transform.get_geo_offset().get_x()
        pixel_offset_x = transform.get_pixel_offset().get_x()
        scale = transform.get_scale()
        return (self._x * BASE_SCALE - geo_offset_x) * scale + pixel_offset_x

    def get_y(self, transform: TRANSFORM_MAYBE = None) -> float:
        """Get the vertical pixel coordinate for this geographic point.

        Args:
            transform: Map view (transformation) to use in finding this coordinate.

        Returns:
            Converted y position in pixels.
        """
        if transform is None:
            return self._y * BASE_SCALE

        geo_offset_y = transform.get_geo_offset().get_y()
        pixel_offset_y = transform.get_pixel_offset().get_y()
        scale = transform.get_scale()
        return (self._y * BASE_SCALE - geo_offset_y) * scale + pixel_offset_y

    def get_longitude(self) -> float:
        """Get the longitude of this point.

        Returns:
            The longitude of this point in degrees.
        """
        return self._longitude

    def get_latitude(self) -> float:
        """Get the latitude of this point.

        Returns:
            The latitude of this point in degrees.
        """
        return self._latitude

    def _longitude_to_x(self, longitude: float) -> float:
        return math.radians(longitude) * RADIUS_MAJOR

    def _latitude_to_y(self, latitude: float) -> float:
        if latitude > 89.9:
            latitude = 89.9
        elif latitude < -89.9:
            latitude = -89.9

        return -1.0 * math.log(math.tan(
            math.pi / 4.0 + math.radians(latitude) / 2.0
        )) * RADIUS_MAJOR


class GeoPolygon:
    """Collection of GeoPoints."""

    def __init__(self, points: typing.List[GeoPoint]):
        """Create a new polygon make up of GeoPoints.

        Args:
            points: The points in this closed polygon.
        """
        self._points = points

    def get_points(self) -> typing.List[GeoPoint]:
        """Get the points in this polygon.

        Returns:
            List of points in this geographic polygon.
        """
        return self._points

    def to_shape(self, transform: TRANSFORM_MAYBE = None) -> sketchingpy.shape_struct.Shape:
        """Convert this GeoPolygon to a closed shape in pixel-space.

        Args:
            transform: The transformation or "map view" to use in finding pixel coordinates.

        Returns:
            Closed shape after projection to pixels.
        """
        def make_tuple(target: GeoPoint) -> typing.Tuple[float, float]:
            return (target.get_x(transform=transform), target.get_y(transform=transform))

        flat_tuples = [make_tuple(point) for point in self._points]

        shape = sketchingpy.shape_struct.Shape(flat_tuples[0][0], flat_tuples[0][1])
        for point in flat_tuples[1:]:
            shape.add_line_to(point[0], point[1])
        shape.close()

        return shape


class GeoTransformation:
    """Description of a geographic transfomration or "map view" to use in projections."""

    def __init__(self, geo_offset: GeoPoint, pixel_offset: PixelOffset, scale: float):
        """Create a new map view record.

        Args:
            geo_offset: The center of the map view in terms of longitude and latitude.
            pixel_offset: Where to place the map view in the sketch in terms of pixels.
            scale: The map zoom level.
        """
        self._geo_offset = geo_offset
        self._pixel_offset = pixel_offset
        self._scale = scale

    def get_geo_offset(self) -> GeoPoint:
        """Get the map center in terms of longitude and latitude.

        Returns:
            The center of the map view in terms of longitude and latitude.
        """
        return self._geo_offset

    def get_pixel_offset(self) -> PixelOffset:
        """Get the center of this map within the sketch's pixel coordinates.

        Returns:
            Where to place the map view in the sketch in terms of pixels.
        """
        return self._pixel_offset

    def get_scale(self) -> float:
        """Get the map scale factor.

        Returns:
            The map zoom level.
        """
        return self._scale


class GeoPolygonBuilder:
    """Builder to create Shapes by way of GeoPolygons and GeoTransformations."""

    def __init__(self, longitude: float, latitude: float,
        transform_getter: typing.Callable[[], TRANSFORM_MAYBE]):
        """Start a builder with a single point.

        Args:
            longitude: The longitude of the starting point in degrees.
            latitude: The latitude of the starting point in degrees.
            transform_getter: Function to call to get the transform to use when converting to shape.
        """
        self._points = [GeoPoint(longitude, latitude)]
        self._transform_getter = transform_getter

    def add_coordinate(self, longitude: float, latitude: float):
        """Add a geographic point to this polygon.

        Draw a line from the last point to a new position where this new point is defined
        geographically in degrees.

        Args:
            longitude: The longitude of the next point in degrees.
            latitude: The latitude of the next point in degrees.
        """
        self._points.append(GeoPoint(longitude, latitude))

    def to_shape(self) -> sketchingpy.shape_struct.Shape:
        """Convert this GeoPolygon to a closed shape in pixel-space.

        Convert this GeoPolygon to a closed shape in pixel-space using the current map view /
        geospatial transformation configuration.

        Returns:
            Closed shape after projection to pixels.
        """
        polygon = GeoPolygon(self._points)
        transform = self._transform_getter()
        return polygon.to_shape(transform)


def parse_geojson(source: typing.Dict) -> typing.List[typing.List[typing.Tuple[float, float]]]:
    """Utility to parse GeoJSON into a series of GeoPolygons.

    Utility to parse GeoJSON into a series of GeoPolygons which currently only supports MultiPolygon
    and Polygon.

    Args:
        source: The loaded GeoJSON source to parse.

    Returns:
        Points of polygons found withing the GeoJSON source.
    """
    all_shapes = []

    for feature in source['features']:
        geometry = feature['geometry']

        feature_shapes: typing.Iterable = []
        if geometry['type'] == 'MultiPolygon':
            feature_shapes = itertools.chain(*geometry['coordinates'])
        elif geometry['type'] == 'Polygon':
            feature_shapes = [geometry['coordinates'][0]]
        else:
            raise RuntimeError('Only support for MultiPolygon and Polygon.')

        for shape in feature_shapes:
            points = [(float(x[0]), float(x[1])) for x in shape]
            all_shapes.append(points)

    return all_shapes
