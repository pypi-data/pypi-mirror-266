import datetime

from tests.utils.tests_utils import test_function

from geoformat.processing.data.union import (
    union_metadata,
    union_geolayer
)

from geoformat.conf.error_messages import (
    metadata_fields_not_same,
    metadata_geometry_crs
)
from tests.data.fields_metadata import geolayer_data_fields_metadata_complete

from tests.data.metadata import metadata_fr_dept_data_and_geometry, metadata_paris_velib

from tests.data.geolayers import (
    geolayer_btc_price_sample,
    geolayer_btc_price_sample_a,
    geolayer_btc_price_sample_b,
    geolayer_btc_price_sample_c,
)

union_metadata_parameters = {
    0: {
        "metadata_a": metadata_fr_dept_data_and_geometry,
        "metadata_b": metadata_fr_dept_data_and_geometry,
        "metadata_name": metadata_fr_dept_data_and_geometry["name"],
        "feature_serialize": None,
        "return_value": metadata_fr_dept_data_and_geometry,
    },
    1: {
        "metadata_a": metadata_fr_dept_data_and_geometry,
        "metadata_b": metadata_fr_dept_data_and_geometry,
        "metadata_name": "test_metadata",
        "feature_serialize": None,
        "return_value": {
            "name": "test_metadata",
            "fields": {
                "CODE_DEPT": {"type": "String", "width": 2, "index": 0},
                "NOM_DEPT": {"type": "String", "width": 23, "index": 1},
            },
            "geometry_ref": {"type": {"Polygon", "MultiPolygon"}, "crs": 2154},
        },
    },
    2: {
        "metadata_a": metadata_fr_dept_data_and_geometry,
        "metadata_b": metadata_paris_velib,
        "metadata_name": "test_metadata",
        "feature_serialize": None,
        "return_value": metadata_fields_not_same,
    },
    3: {
        "metadata_a": {
            "name": "FRANCE_DPT_GENERALIZE_LAMB93_ROUND_DATA_AND_GEOMETRY",
            "fields": geolayer_data_fields_metadata_complete,
            "geometry_ref": {"type": {"MultiPolygon"}, "crs": 2154},
        },
        "metadata_b": {
            "name": "FRANCE_DPT_GENERALIZE_LAMB93_ROUND_DATA_AND_GEOMETRY",
            "fields": geolayer_data_fields_metadata_complete,
            "geometry_ref": {"type": {"Polygon"}, "crs": 2154},
        },
        "metadata_name": "test_metadata",
        "feature_serialize": None,
        "return_value": {
            "name": "test_metadata",
            "fields": geolayer_data_fields_metadata_complete,
            "geometry_ref": {"type": {"MultiPolygon", "Polygon"}, "crs": 2154},
        }
    },
    4: {
        "metadata_a": {
            "name": "FRANCE_DPT_GENERALIZE_LAMB93_ROUND_DATA_AND_GEOMETRY",
            "fields": geolayer_data_fields_metadata_complete,
            "geometry_ref": {"type": {"MultiPolygon"}, "crs": 2154},
        },
        "metadata_b": {
            "name": "FRANCE_DPT_GENERALIZE_LAMB93_ROUND_DATA_AND_GEOMETRY",
            "fields": geolayer_data_fields_metadata_complete,
            "geometry_ref": {"type": {"Polygon"}, "crs": 4326},
        },
        "metadata_name": "test_metadata",
        "feature_serialize": None,
        "return_value": metadata_geometry_crs
    },
    5: {
        "metadata_a": {'name': 'BTC_DAILY_PRICE', 'fields': {'DATE': {'type': 'Date', 'index': 0}, 'DAYS': {'type': 'Integer', 'index': 1}, 'TIMESTAMP': {'type': 'Integer', 'index': 2}, 'USD_PRICE_CLOSE': {'type': 'Real', 'width': 7, 'precision': 2, 'index': 3}, 'PRICE_ESTIMATE_MINUS_1STD': {'type': 'Real', 'width': 22, 'precision': 20, 'index': 4}, 'PRICE_ESTIMATE_MINUS_2STD': {'type': 'Real', 'width': 21, 'precision': 20, 'index': 5}, 'PRICE_ESTIMATE_2019': {'type': 'Real', 'width': 22, 'precision': 20, 'index': 6}, 'PRICE_ESTIMATE': {'type': 'Real', 'width': 22, 'precision': 20, 'index': 7}, 'PRICE_ESTIMATE_PLUS_1STD': {'type': 'Real', 'width': 22, 'precision': 20, 'index': 8}, 'PRICE_ESTIMATE_PLUS_2STD': {'type': 'Real', 'width': 22, 'precision': 20, 'index': 9}}},
        "metadata_b": {'name': 'BTC_DAILY_PRICE', 'fields': {'DATE': {'type': 'Date', 'index': 0}, 'DAYS': {'type': 'Integer', 'index': 1}, 'TIMESTAMP': {'type': 'Integer', 'index': 2}, 'USD_PRICE_CLOSE': {'type': 'Real', 'width': 7, 'precision': 2, 'index': 3}, 'PRICE_ESTIMATE_MINUS_1STD': {'type': 'Real', 'width': 18, 'precision': 15, 'index': 4}, 'PRICE_ESTIMATE_MINUS_2STD': {'type': 'Real', 'width': 18, 'precision': 15, 'index': 5}, 'PRICE_ESTIMATE_2019': {'type': 'Real', 'width': 19, 'precision': 15, 'index': 6}, 'PRICE_ESTIMATE': {'type': 'Real', 'width': 17, 'precision': 14, 'index': 7}, 'PRICE_ESTIMATE_PLUS_1STD': {'type': 'Real', 'width': 17, 'precision': 14, 'index': 8}, 'PRICE_ESTIMATE_PLUS_2STD': {'type': 'Real', 'width': 18, 'precision': 14, 'index': 9}}},
        "metadata_name": "BTC_DAILY_PRICE",
        "feature_serialize": None,
        "return_value": {'name': 'BTC_DAILY_PRICE', 'fields': {'DATE': {'type': 'Date', 'index': 0}, 'DAYS': {'type': 'Integer', 'index': 1}, 'TIMESTAMP': {'type': 'Integer', 'index': 2}, 'USD_PRICE_CLOSE': {'type': 'Real', 'width': 7, 'precision': 2, 'index': 3}, 'PRICE_ESTIMATE_MINUS_1STD': {'type': 'Real', 'width': 22, 'precision': 20, 'index': 4}, 'PRICE_ESTIMATE_MINUS_2STD': {'type': 'Real', 'width': 21, 'precision': 20, 'index': 5}, 'PRICE_ESTIMATE_2019': {'type': 'Real', 'width': 22, 'precision': 20, 'index': 6}, 'PRICE_ESTIMATE': {'type': 'Real', 'width': 22, 'precision': 20, 'index': 7}, 'PRICE_ESTIMATE_PLUS_1STD': {'type': 'Real', 'width': 22, 'precision': 20, 'index': 8}, 'PRICE_ESTIMATE_PLUS_2STD': {'type': 'Real', 'width': 22, 'precision': 20, 'index': 9}}}
    },
}

union_geolayer_parameters = {
    0: {
        "geolayer_list": [geolayer_btc_price_sample_a, geolayer_btc_price_sample_b, geolayer_btc_price_sample_c],
        "geolayer_name": 'BTC_DAILY_PRICE',
        "serialize": False,
        "return_value": {'metadata': {'name': 'BTC_DAILY_PRICE', 'fields': {'DATE': {'type': 'Date', 'index': 0}, 'DAYS': {'type': 'Integer', 'index': 1}, 'TIMESTAMP': {'type': 'Integer', 'index': 2}, 'USD_PRICE_CLOSE': {'type': 'Real', 'width': 7, 'precision': 2, 'index': 3}}}, 'features': {0: {'attributes': {'DATE': datetime.date(2022, 4, 27), 'DAYS': 4865, 'TIMESTAMP': 1651010400, 'USD_PRICE_CLOSE': 39252.04}}, 1: {'attributes': {'DATE': datetime.date(2022, 4, 28), 'DAYS': 4866, 'TIMESTAMP': 1651096800, 'USD_PRICE_CLOSE': 39749.75}}, 2: {'attributes': {'DATE': datetime.date(2022, 4, 29), 'DAYS': 4867, 'TIMESTAMP': 1651183200, 'USD_PRICE_CLOSE': 38594.22}}, 3: {'attributes': {'DATE': datetime.date(2022, 4, 30), 'DAYS': 4868, 'TIMESTAMP': 1651269600, 'USD_PRICE_CLOSE': 37650.13}}, 4: {'attributes': {'DATE': datetime.date(2022, 5, 1), 'DAYS': 4869, 'TIMESTAMP': 1651356000, 'USD_PRICE_CLOSE': 38480.53}}, 5: {'attributes': {'DATE': datetime.date(2022, 5, 2), 'DAYS': 4870, 'TIMESTAMP': 1651442400, 'USD_PRICE_CLOSE': 38513.01}}, 6: {'attributes': {'DATE': datetime.date(2022, 5, 3), 'DAYS': 4871, 'TIMESTAMP': 1651528800, 'USD_PRICE_CLOSE': 37725.38}}, 7: {'attributes': {'DATE': datetime.date(2022, 5, 4), 'DAYS': 4872, 'TIMESTAMP': 1651615200, 'USD_PRICE_CLOSE': 39680.21}}, 8: {'attributes': {'DATE': datetime.date(2022, 5, 5), 'DAYS': 4873, 'TIMESTAMP': 1651701600, 'USD_PRICE_CLOSE': 36546.86}}, 9: {'attributes': {'DATE': datetime.date(2022, 5, 6), 'DAYS': 4874, 'TIMESTAMP': 1651788000, 'USD_PRICE_CLOSE': 36009.89}}, 10: {'attributes': {'DATE': datetime.date(2022, 5, 7), 'DAYS': 4875, 'TIMESTAMP': 1651874400, 'USD_PRICE_CLOSE': 35469.21}}, 11: {'attributes': {'DATE': datetime.date(2022, 5, 8), 'DAYS': 4876, 'TIMESTAMP': 1651960800, 'USD_PRICE_CLOSE': 34033.77}}, 12: {'attributes': {'DATE': datetime.date(2022, 5, 9), 'DAYS': 4877, 'TIMESTAMP': 1652047200, 'USD_PRICE_CLOSE': 30076.9}}, 13: {'attributes': {'DATE': datetime.date(2022, 5, 10), 'DAYS': 4878, 'TIMESTAMP': 1652133600, 'USD_PRICE_CLOSE': 31013.12}}, 14: {'attributes': {'DATE': datetime.date(2022, 5, 11), 'DAYS': 4879, 'TIMESTAMP': 1652220000, 'USD_PRICE_CLOSE': 28590.66}}, 15: {'attributes': {'DATE': datetime.date(2022, 5, 12), 'DAYS': 4880, 'TIMESTAMP': 1652306400, 'USD_PRICE_CLOSE': 28915.72}}, 16: {'attributes': {'DATE': datetime.date(2022, 5, 13), 'DAYS': 4881, 'TIMESTAMP': 1652392800, 'USD_PRICE_CLOSE': 29244.83}}, 17: {'attributes': {'DATE': datetime.date(2022, 5, 14), 'DAYS': 4882, 'TIMESTAMP': 1652479200, 'USD_PRICE_CLOSE': 30050.31}}, 18: {'attributes': {'DATE': datetime.date(2022, 5, 15), 'DAYS': 4883, 'TIMESTAMP': 1652565600, 'USD_PRICE_CLOSE': 31296.11}}, 19: {'attributes': {'DATE': datetime.date(2022, 5, 16), 'DAYS': 4884, 'TIMESTAMP': 1652652000, 'USD_PRICE_CLOSE': 29838.5}}, 20: {'attributes': {'DATE': datetime.date(2022, 5, 17), 'DAYS': 4885, 'TIMESTAMP': 1652738400, 'USD_PRICE_CLOSE': 30415.91}}, 21: {'attributes': {'DATE': datetime.date(2022, 5, 18), 'DAYS': 4886, 'TIMESTAMP': 1652824800, 'USD_PRICE_CLOSE': None}}, 22: {'attributes': {'DATE': datetime.date(2022, 5, 19), 'DAYS': 4887, 'TIMESTAMP': 1652911200}}}}
    }
}


def test_all():
    # union_metadata
    print(test_function(union_metadata, union_metadata_parameters))

    # union geolayer
    print(test_function(union_geolayer, union_geolayer_parameters))


if __name__ == "__main__":
    test_all()
