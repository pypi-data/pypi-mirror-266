import pytest
from geoformat.conversion.coordinates_conversion import separate_coordinates_dimensions

from tests.data.coordinates import (
    point_coordinates,
    point_coordinates_3d,
    linestring_coordinates,
    linestring_coordinates_3d,
    polygon_coordinates,
    multipolygon_coordinates,
    polygon_coordinates_3d,
    multipolygon_coordinates_3d
)


class Test_separate_coordinates_dimensions:

    @pytest.mark.parametrize("input_coordinates,expected_output", [
        (point_coordinates, [[[-115.81]], [[37.24]]]),
        (linestring_coordinates, [[[8.919], [8.923]], [[44.4074], [44.4075]]]),
        (polygon_coordinates,
         [[[[2.38], [23.194], [-120.43], [2.38]], [[-5.21], [15.21], [-20.51], [-5.21]]],
          [[[57.322], [-20.28], [19.15], [57.322]], [[23.51], [-10.81], [1.51], [23.51]]]]),
        (multipolygon_coordinates,
         [[[[[3.78], [-130.91], [35.12], [3.78]]], [[[23.18], [-1.31], [3.41], [23.18]]]],
          [[[[9.28], [1.52], [72.234], [9.28]]], [[[-34.29], [-4.61], [77.91], [-34.29]]]]]),
        (point_coordinates_3d, [[[-115.81]], [[37.24]], [[-38.654]]]),
        (linestring_coordinates_3d, [[[8.919], [8.923]], [[44.4074], [44.4075]], [[254.8], [-98]]]),
        (polygon_coordinates_3d, [[[[2.38], [23.194], [-120.43], [2.38]], [[-5.21], [15.21], [-20.51], [-5.21]]],
                                  [[[57.322], [-20.28], [19.15], [57.322]], [[23.51], [-10.81], [1.51], [23.51]]],
                                  [[[-76.65], [145], [0.146], [78.89]], [[154.4], [None], [-32.6], [45.6]]]]),
        (multipolygon_coordinates_3d, [[[[[3.78], [-130.91], [35.12], [3.78]]], [[[23.18], [-1.31], [3.41], [23.18]]]],
                                       [[[[9.28], [1.52], [72.234], [9.28]]], [[[-34.29], [-4.61], [77.91], [-34.29]]]],
                                       [[[[123], [15.54], [78.6], [87.878]]],
                                        [[[-45.1515], [-3.245], [-41.0], [-87.89]]]]]),

    ])
    def test_coordinates_conversion(self, input_coordinates, expected_output):
        assert separate_coordinates_dimensions(input_coordinates) == expected_output
