import unittest

import sketchingpy.geo


class GeoTests(unittest.TestCase):

    def setUp(self):
        # Center the map on San Francisco and place in middle of sketch
        center_longitude = -122.418343
        center_latitude = 37.761842
        center_x = 250
        center_y = 250
        map_scale = 100

        # Create a geo transformation that ties pixel to geo coordinates
        self._transformation = sketchingpy.geo.GeoTransformation(
            sketchingpy.geo.GeoPoint(center_longitude, center_latitude),  # Where to center geographically
            sketchingpy.geo.PixelOffset(center_x, center_y),  # Where to center in terms of pixels
            map_scale  # How much zoom
        )


    def test_point(self):
        point = sketchingpy.geo.GeoPoint(-122.262938, 37.873139)
        self.assertAlmostEqual(point.get_x(transform=self._transformation), 422.9960546672828)
        self.assertAlmostEqual(point.get_y(transform=self._transformation), 93.16413302587421)

    def test_polygon(self):
        points = [
            sketchingpy.geo.GeoPoint(-122, 38),
            sketchingpy.geo.GeoPoint(-121, 38),
            sketchingpy.geo.GeoPoint(-121, 37),
            sketchingpy.geo.GeoPoint(-122, 37)
        ]
        geo_polygon = sketchingpy.geo.GeoPolygon(points)
        shape = geo_polygon.to_shape(transform=self._transformation)
        self.assertAlmostEqual(shape.get_start_x(), 715.6972973692973)
        self.assertAlmostEqual(shape.get_start_y(), -85.89322991684298)

    def test_parse_geojson(self):
        test_source = {
            'features': [{
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[
                        [-122, 38],
                        [-121, 38],
                        [-121, 37],
                        [-122, 37],
                    ]]
                }
            }]
        }
        polygons = sketchingpy.geo.parse_geojson(test_source)

        self.assertEqual(len(polygons), 1)
        polygon = polygons[0]

        self.assertEqual(len(polygon), 4)
        first_point = polygon[0]
        self.assertAlmostEqual(first_point[0], -122)
        self.assertAlmostEqual(first_point[1], 38)
