from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path

from geoformat.conversion.coordinates_conversion import force_rhr_polygon_coordinates
from geoformat.conversion.geometry_conversion import geometry_to_bbox
from geoformat.geoprocessing.merge_geometries import merge_geometries

class DrawGeometry:

    def __init__(self, geometry: Dict) -> None:
        """
        Initializes the DrawGeometry class with geometry data and optional styling.

        :param geometry: A dictionary representing the geometric data to plot.
        """
        self.geometry = geometry
        self.bbox = geometry.get("bbox") or geometry_to_bbox(geometry=self.geometry)
        self.fig, self.ax = plt.subplots()

    def create_codes(self, num_points: int) -> List[int]:
        """
        Creates a list of Path codes for constructing a geometry path.

        :param num_points: The number of points in the geometry.
        :return: A list of Matplotlib Path codes.
        """
        return [Path.MOVETO] + [Path.LINETO] * (num_points - 1)

    def validate_coordinates(self, coordinates: List[List[float]]) -> bool:
        """
        Validates the provided coordinates to ensure they are non-empty and plotable.

        :param coordinates: The coordinates to validate.
        :return: True if the coordinates are valid, False otherwise.
        """
        if coordinates:
            if isinstance(coordinates[0], (list, tuple)):
                return any(coords for coords in coordinates)
            return True
        return False

    def plot_point(self, coordinates: List[float]) -> None:
        """
        Plots a single point on the ax object.

        :param coordinates: A list containing the x and y coordinates of the point.
        """
        matplolib_point_style = {
            "marker": 'o',
            "markersize": 5,
            "markeredgecolor": 'black',
            "markerfacecolor": 'red',
            "markeredgewidth": 1,
            "linestyle": None,
            "linewidth": None,
            "zorder": 2,
            "alpha": 1,
            "antialiased": True,
        }

        self.ax.plot(coordinates[0], coordinates[1], **matplolib_point_style)

    def plot_line_string(self, coordinates: List[List[float]]) -> None:
        """
        Plots a single LineString geometry.

        :param coordinates: A list of [x, y] pairs representing the LineString's vertices.
        """
        matplotlib_linestring_style = {
            "edgecolor": 'black',
            "facecolor": "none",
            "linewidth": 1,
            "linestyle": '-',
            "zorder": 1,
            "alpha": 1,
            "antialiased": True,
        }
        verts = np.array(coordinates)
        path = Path(verts)
        patch = PathPatch(path, **matplotlib_linestring_style)
        self.ax.add_patch(patch)

    def plot_polygon(self, coordinates: List[List[List[float]]]) -> None:
        """
        Processes and plots polygon geometry with the given coordinates.

        :param coordinates: A nested list representing the polygon's outer boundary and any inner holes.
        """
        matplotlib_polygon_style = {
            "edgecolor": 'black',
            "facecolor": "#d8e0ea",
            "linewidth": 1,
            "linestyle": '-',
            "zorder": 0,
            "alpha": 1,
            "antialiased": True,
        }
        coordinates = force_rhr_polygon_coordinates(coordinates=coordinates)
        verts = None
        codes = []

        for ring in coordinates:
            ring_verts = np.array(ring)
            if verts is None:
                verts = ring_verts
            else:
                verts = np.concatenate([verts, ring_verts])
            codes += self.create_codes(len(ring))

        path = Path(verts, codes)
        patch = PathPatch(path, **matplotlib_polygon_style)
        self.ax.add_patch(patch)

    def plot_multi_point(self, coordinates: List[List[float]]) -> None:
        """Plots a MultiPoint geometry."""
        for pt in coordinates:
            if pt:
                self.plot_point(pt)

    def plot_multi_line_string(self, coordinates: List[List[List[float]]]) -> None:
        """Plots a MultiLineString geometry."""
        for ls in coordinates:
            if ls:
                self.plot_line_string(ls)

    def plot_multi_polygon(self, coordinates: List[List[List[List[float]]]]) -> None:
        """Plots a MultiPolygon geometry."""
        for poly in coordinates:
            if poly:
                self.plot_polygon(poly)

    def plot_geometry(self, geometry: Dict) -> None:
        """
        Plots the provided geometry based on its type.

        :param geometry: The geometry dictionary to plot.
        """
        geometry_type = geometry['type']
        geometry_handlers = {
            'Point': self.plot_point,
            'MultiPoint': self.plot_multi_point,
            'LineString': self.plot_line_string,
            'MultiLineString': self.plot_multi_line_string,
            'Polygon': self.plot_polygon,
            'MultiPolygon': self.plot_multi_polygon
        }

        if geometry_type in geometry_handlers:
            handler = geometry_handlers[geometry_type]
            coordinates = geometry.get('coordinates', [])
            if self.validate_coordinates(coordinates=coordinates) is True:
                handler(coordinates=coordinates)

    def expand_bbox(self) -> Tuple[float, float, float, float]:
        """
        Expands the bounding box by a margin.

        :return: An expanded bounding box.
        """
        if self.bbox:
            x_diff = self.bbox[2] - self.bbox[0]
            y_diff = self.bbox[3] - self.bbox[1]

            x_margin = x_diff * 0.1 or 1
            y_margin = y_diff * 0.1 or 1
            expand_bbox = self.bbox[0] - x_margin, self.bbox[1] - y_margin, self.bbox[2] + x_margin, self.bbox[
                3] + y_margin
        else:
            expand_bbox = (-1, -1, 1, 1)

        return expand_bbox

    def plot(self, graticule=False) -> None:
        """
        Main method to plot the provided geometry and apply custom style if provided.
        """
        # plot geometry and apply style
        if self.geometry['type'] == 'GeometryCollection':
            for geometry in self.geometry['geometries']:
                self.plot_geometry(geometry)
        else:
            self.plot_geometry(self.geometry)

        # add margin
        margin = self.expand_bbox()
        self.ax.set_xlim(margin[0], margin[2])
        self.ax.set_ylim(margin[1], margin[3])

        # add grid
        if graticule is True:
            self.ax.minorticks_on()
            self.ax.grid(which='major', color='black', linestyle='-', linewidth=0.5, alpha=0.5)
            self.ax.grid(which='minor', color='gray', linestyle=':', linewidth=0.2, alpha=0.5)

        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()


def draw_geometry(geometry: Dict, graticule=False) -> None:
    """
    Plots a given geometry using the DrawGeometry class.

    :param geometry: A dictionary representing the geometric data to plot.
    :param graticule: add graticule for better geometry location
    """
    DrawGeometry(geometry=geometry).plot(graticule=graticule)


def draw_feature(feature: Dict, graticule=False) -> None:
    """
    Draws the geometry of a given feature using the DrawGeometry class.

    This function extracts the "geometry" key from the provided feature dictionary and
    plots it.

    :param feature: A dictionary representing a geographic feature, which must include a
                    "geometry" key containing geometric data to plot.
    :param graticule: add graticule for better geometry location
    """
    feature_geometry = feature.get("geometry")
    if feature_geometry:
        draw_geometry(geometry=feature_geometry, graticule=graticule)


def draw_geolayer(geolayer: Dict, graticule=False) -> None:
    """
    Iterates over features in a geolayer, merges their geometries, and plots the combined geometry.

    Each feature's geometry within the geolayer is merged into a single geometry, which is then plotted.

    :param geolayer: A Geolayer dict
    :param graticule: add graticule for better geometry location
    """
    geolayer_geometry = None
    for i_feat, feature in geolayer["features"].items():
        feature_geometry = feature.get('geometry')
        if feature_geometry:
            if geolayer_geometry is None:
                geolayer_geometry = feature_geometry
            else:
                geolayer_geometry = merge_geometries(geolayer_geometry, feature_geometry)

    draw_geometry(geometry=geolayer_geometry, graticule=graticule)

if __name__ == '__main__':
    #
    from tests.data.geometries import (
        POINT,
        POINT_EMPTY,
        MULTIPOINT,
        MULTIPOINT_EMPTY,
        LINESTRING,
        LINESTRING_EMPTY,
        POLYGON,
        POLYGON_EMPTY,
        MULTILINESTRING,
        MULTILINESTRING_EMPTY,
        MULTIPOLYGON,
        MULTIPOLYGON_EMPTY,
        GEOMETRYCOLLECTION,
        GEOMETRYCOLLECTION_EMPTY,
        LINESTRING_loire,
        LINESTRING_loire_3857,
        MULTILINESTRING_loire_katsuragawa_river_3857,
        GEOMETRYCOLLECTION_paris_tokyo_loire_katsuragawa_river_france_japan
    )

    DrawGeometry(POINT_EMPTY).plot(graticule=True)
    DrawGeometry(MULTIPOINT_EMPTY).plot(graticule=True)
    DrawGeometry(LINESTRING_EMPTY).plot(graticule=True)
    DrawGeometry(MULTILINESTRING_EMPTY).plot(graticule=True)
    DrawGeometry(POLYGON_EMPTY).plot(graticule=True)
    DrawGeometry(MULTIPOLYGON_EMPTY).plot(graticule=True)
    DrawGeometry(POINT).plot(graticule=True)
    DrawGeometry(MULTIPOINT).plot(graticule=True)
    DrawGeometry(LINESTRING).plot(graticule=True)
    DrawGeometry(MULTILINESTRING).plot(graticule=True)
    DrawGeometry(MULTIPOLYGON).plot(graticule=True)
    DrawGeometry(POLYGON).plot(graticule=True)
    DrawGeometry(GEOMETRYCOLLECTION_paris_tokyo_loire_katsuragawa_river_france_japan).plot(graticule=True)
    DrawGeometry(GEOMETRYCOLLECTION).plot(graticule=True)
    DrawGeometry(GEOMETRYCOLLECTION_EMPTY).plot(graticule=True)
    DrawGeometry(LINESTRING_loire).plot(graticule=True)
    DrawGeometry(LINESTRING_loire_3857).plot(graticule=True)
    DrawGeometry(MULTILINESTRING_loire_katsuragawa_river_3857).plot(graticule=True)

    polygon_test_coordinates = [
        [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]],
        [[0.1, 0.6], [0.1, 0.9], [0.4, 0.9], [0.4, 0.6], [0.1, 0.6]],
        [[0.6, 0.1], [0.6, 0.4], [0.9, 0.4], [0.9, 0.1], [0.6, 0.1]],
        [[0.6, 0.6], [0.6, 0.9], [0.9, 0.9], [0.9, 0.6], [0.6, 0.6]],
        [[0.1, 0.1], [0.1, 0.4], [0.4, 0.4], [0.4, 0.1], [0.1, 0.1]]

    ]

    polygon_triangle_test_coordinates = [
        [[0, 0], [0.5, 1], [1, 0], [0, 0]],
        [[0.1, 0.1], [0.3, 0.5], [0.5, 0.1], [0.1, 0.1]],
        [[0.5, 0.1], [0.7, 0.5], [0.9, 0.1], [0.5, 0.1]],
        [[0.3, 0.5], [0.5, 0.9], [0.7, 0.5], [0.3, 0.5]]
    ]

    # from geoformat.conversion.coordinates_conversion import format_coordinates
    #
    # polygon_triangle_test_coordinates_translate = format_coordinates(
    #     coordinates_list_tuple=polygon_triangle_test_coordinates, translate=(2, -1))
    #
    # print("polygon_triangle_test_coordinates_translate", polygon_triangle_test_coordinates_translate)
    #
    # multipolygon_test_coordinates = [polygon_test_coordinates, polygon_triangle_test_coordinates_translate]
    #
    # polygon_geometry = {"type": "Polygon", "coordinates": polygon_triangle_test_coordinates_translate}
    # multipolygon_geometry = {"type": "MultiPolygon", "coordinates": multipolygon_test_coordinates}
    # geometry = multipolygon_geometry
    # print(geometry)
    # DrawGeometry(geometry).plot(grid=True)

    # # # Example usage with Point:
    # geojson_point = {
    #     'type': 'Point',
    #     'coordinates': [-115.81, 37.24]
    # }
    #
    # # Example usage with MultiPoint:
    # geojson_multi_point = {
    #     'type': 'MultiPoint',
    #     'coordinates': [[-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]]
    # }
    #
    #
    # # Example usage with LineString:
    # geojson_line_string = {
    #     'type': 'LineString',
    #     'coordinates': [[8.919, 44.4074], [8.923, 44.4075]]
    # }
    #
    # # Example usage with MultiLineString:
    # geojson_multi_line_string = {
    #     'type': 'MultiLineString',
    #     'coordinates': [[[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]]
    # }
    #
    #
    # # Example usage with MultiPolygon:
    # geojson_multipolygon = {
    #     'type': 'MultiPolygon',
    #     'coordinates': [
    #         [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]],
    #         [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]
    #     ]
    # }
    #
    #
    # # Example usage with Polygon:
    # geojson_polygon = {
    #     'type': 'Polygon',
    #     'coordinates': [
    #         [[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],  # Exterior contour
    #         [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]  # Hole
    #     ]
    # }

    # TODO add docstring and add in geoformat __init : force_rhr_polygon_coordinates


    from tests.data.geolayers import geolayer_idf_reseau_ferre, geolayer_france_japan
    from tests.data.features import (feature_france)
    draw_geolayer(geolayer=geolayer_france_japan, graticule=True)
    draw_feature(feature=feature_france, graticule=True)
    draw_geometry(geometry=feature_france['geometry'], graticule=True)