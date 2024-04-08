from geoformat.conversion.feature_conversion import feature_serialize

from geoformat.conversion.geolayer_conversion import (
    create_geolayer_from_i_feat_list,
    reproject_geolayer,
    multi_geometry_to_single_geometry_geolayer,
    geolayer_to_2d_geolayer,
)
from tests.data.fields_metadata import geolayer_data_fields_metadata_complete
from tests.data.geolayers import (
    geolayer_fr_dept_data_only,
    geolayer_fr_dept_data_and_geometry,
    geolayer_fr_dept_data_and_geometry_4326_precision_6,
    geolayer_geometry_2d,
    geolayer_geometry_3d,
    geolayer_geometry_only_all_geometries_type,
    feature_list_data_and_geometry_geolayer,
)
from tests.utils.tests_utils import test_function

geolayer_to_2d_geolayer_parameters = {
    0: {
        "input_geolayer": geolayer_fr_dept_data_only,
        "return_value": geolayer_fr_dept_data_only,
    },
    1: {
        "input_geolayer": geolayer_fr_dept_data_and_geometry,
        "return_value": geolayer_fr_dept_data_and_geometry,
    },
    2: {
        "input_geolayer": geolayer_geometry_3d,
        "return_value": geolayer_geometry_2d,
    },
}

create_geolayer_from_i_feat_list_parameters = {
    0: {
        "geolayer": geolayer_fr_dept_data_only,
        "i_feat_list": 0,
        "serialize": False,
        "reset_i_feat": True,
        "return_value": {
            "metadata": {
                "fields": geolayer_data_fields_metadata_complete,
                "name": "FRANCE_DPT_GENERALIZE_LAMB93_ROUND_DATA_ONLY",
            },
            "features": {0: {"attributes": {"CODE_DEPT": "32", "NOM_DEPT": "GERS"}}},
        },
    },
    1: {
        "geolayer": geolayer_fr_dept_data_only,
        "i_feat_list": [0],
        "serialize": False,
        "reset_i_feat": True,
        "return_value": {
            "metadata": {
                "fields": geolayer_data_fields_metadata_complete,
                "name": "FRANCE_DPT_GENERALIZE_LAMB93_ROUND_DATA_ONLY",
            },
            "features": {0: {"attributes": {"CODE_DEPT": "32", "NOM_DEPT": "GERS"}}},
        },
    },
    2: {
        "geolayer": geolayer_fr_dept_data_only,
        "i_feat_list": [0, 95],
        "serialize": False,
        "reset_i_feat": True,
        "return_value": {
            "metadata": {
                "fields": geolayer_data_fields_metadata_complete,
                "name": "FRANCE_DPT_GENERALIZE_LAMB93_ROUND_DATA_ONLY",
            },
            "features": {
                0: {"attributes": {"CODE_DEPT": "32", "NOM_DEPT": "GERS"}},
                1: {"attributes": {"CODE_DEPT": "93", "NOM_DEPT": "SEINE-SAINT-DENIS"}},
            },
        },
    },
    3: {
        "geolayer": geolayer_fr_dept_data_only,
        "i_feat_list": [0, 95],
        "serialize": False,
        "reset_i_feat": False,
        "return_value": {
            "metadata": {
                "fields": geolayer_data_fields_metadata_complete,
                "name": "FRANCE_DPT_GENERALIZE_LAMB93_ROUND_DATA_ONLY",
            },
            "features": {
                0: {"attributes": {"CODE_DEPT": "32", "NOM_DEPT": "GERS"}},
                95: {
                    "attributes": {"CODE_DEPT": "93", "NOM_DEPT": "SEINE-SAINT-DENIS"}
                },
            },
        },
    },
    4: {
        "geolayer": geolayer_fr_dept_data_only,
        "i_feat_list": [0, 95],
        "serialize": True,
        "reset_i_feat": False,
        "return_value": {'metadata': {'name': 'FRANCE_DPT_GENERALIZE_LAMB93_ROUND_DATA_ONLY', 'fields': {'CODE_DEPT': {'type': 'String', 'width': 2, 'index': 0}, 'NOM_DEPT': {'type': 'String', 'width': 23, 'index': 1}}, 'feature_serialize': True}, 'features': {0: {'attributes': "{'CODE_DEPT': '32', 'NOM_DEPT': 'GERS'}"}, 95: {'attributes': "{'CODE_DEPT': '93', 'NOM_DEPT': 'SEINE-SAINT-DENIS'}"}}},
    },
}

reproject_geolayer_parameters = {
    0: {
        "geolayer": geolayer_fr_dept_data_and_geometry,
        "out_crs": 4326,
        "in_crs": None,
        "precision": 6,
        "return_value": geolayer_fr_dept_data_and_geometry_4326_precision_6,
    },
    1: {
        "geolayer": geolayer_fr_dept_data_and_geometry,
        "out_crs": 4326,
        "in_crs": 2154,
        "precision": 6,
        "return_value": geolayer_fr_dept_data_and_geometry_4326_precision_6,
    },
}

multi_geometry_to_single_geometry_geolayer_parameters = {
    0: {
        "geolayer": geolayer_geometry_only_all_geometries_type,
        "return_value": {'metadata': {'name': 'all_geometry_type_only', 'geometry_ref': {'type': {'Point', 'Polygon', 'LineString'}, 'crs': 4326}}, 'features': {0: {'geometry': {'type': 'Point', 'coordinates': [-115.81, 37.24]}}, 1: {'geometry': {'type': 'Point', 'coordinates': []}}, 2: {'geometry': {'type': 'LineString', 'coordinates': [[8.919, 44.4074], [8.923, 44.4075]]}}, 3: {'geometry': {'type': 'LineString', 'coordinates': []}}, 4: {'geometry': {'type': 'Polygon', 'coordinates': [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]]}}, 5: {'geometry': {'type': 'Polygon', 'coordinates': []}}, 6: {'geometry': {'type': 'Point', 'coordinates': [-155.52, 19.61]}}, 7: {'geometry': {'type': 'Point', 'coordinates': [-156.22, 20.74]}}, 8: {'geometry': {'type': 'Point', 'coordinates': [-157.97, 21.46]}}, 9: {'geometry': {'type': 'LineString', 'coordinates': [[3.75, 9.25], [-130.95, 1.52]]}}, 10: {'geometry': {'type': 'LineString', 'coordinates': [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]}}, 11: {'geometry': {'type': 'Polygon', 'coordinates': [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]]}}, 12: {'geometry': {'type': 'Polygon', 'coordinates': [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]}}, 13: {'geometry': {'type': 'Point', 'coordinates': [-115.81, 37.24]}}, 14: {'geometry': {'type': 'LineString', 'coordinates': [[8.919, 44.4074], [8.923, 44.4075]]}}, 15: {'geometry': {'type': 'Polygon', 'coordinates': [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]]}}, 16: {'geometry': {'type': 'Point', 'coordinates': [-155.52, 19.61]}}, 17: {'geometry': {'type': 'Point', 'coordinates': [-156.22, 20.74]}}, 18: {'geometry': {'type': 'Point', 'coordinates': [-157.97, 21.46]}}, 19: {'geometry': {'type': 'LineString', 'coordinates': [[3.75, 9.25], [-130.95, 1.52]]}}, 20: {'geometry': {'type': 'LineString', 'coordinates': [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]}}, 21: {'geometry': {'type': 'Polygon', 'coordinates': [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]]}}, 22: {'geometry': {'type': 'Polygon', 'coordinates': [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]}}, 23: {'geometry': {'type': 'Point', 'coordinates': []}}, 24: {'geometry': {'type': 'LineString', 'coordinates': [[8.919, 44.4074], [8.923, 44.4075]]}}, 25: {'geometry': {'type': 'Polygon', 'coordinates': [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]]}}, 26: {'geometry': {'type': 'LineString', 'coordinates': [[3.75, 9.25], [-130.95, 1.52]]}}, 27: {'geometry': {'type': 'LineString', 'coordinates': [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]}}}},
    },
    1: {
        "geolayer": feature_list_data_and_geometry_geolayer,
        "return_value": {'metadata': {'name': 'data_and_geometries', 'fields': {'CODE_DEPT': {'type': 'String', 'width': 2, 'index': 0}, 'NOM_DEPT': {'type': 'String', 'width': 10, 'index': 1}}, 'geometry_ref': {'type': {'Polygon'}, 'crs': 2154}}, 'features': {0: {'attributes': {'CODE_DEPT': '53', 'NOM_DEPT': 'MAYENNE'}, 'geometry': {'type': 'Polygon', 'coordinates': [[[399495.0, 6830885.0], [398130.0, 6822559.0], [400321.0, 6810723.0], [395852.0, 6803336.0], [398626.0, 6784333.0], [400465.0, 6781914.0], [400197.0, 6773697.0], [394099.0, 6773357.0], [390140.0, 6770978.0], [386941.0, 6760260.0], [382932.0, 6754022.0], [389872.0, 6749698.0], [393110.0, 6750366.0], [402067.0, 6747685.0], [404251.0, 6751414.0], [412442.0, 6746090.0], [419671.0, 6744167.0], [429458.0, 6743442.0], [440863.0, 6746201.0], [446732.0, 6745443.0], [446459.0, 6750432.0], [442128.0, 6753611.0], [448124.0, 6758669.0], [447308.0, 6764356.0], [455060.0, 6767070.0], [451057.0, 6776681.0], [459373.0, 6778102.0], [460615.0, 6783387.0], [458409.0, 6789055.0], [466280.0, 6794064.0], [465298.0, 6799724.0], [467628.0, 6811401.0], [473893.0, 6813452.0], [474394.0, 6821359.0], [467262.0, 6822174.0], [466087.0, 6830999.0], [463434.0, 6833996.0], [457920.0, 6827997.0], [451256.0, 6826715.0], [446687.0, 6829012.0], [441174.0, 6828584.0], [437568.0, 6825109.0], [429868.0, 6822252.0], [422197.0, 6821752.0], [414934.0, 6829326.0], [407934.0, 6831360.0], [404267.0, 6828490.0], [399495.0, 6830885.0]]]}}, 1: {'attributes': {'CODE_DEPT': '02', 'NOM_DEPT': 'AISNE'}, 'geometry': {'type': 'Polygon', 'coordinates': [[[776081.0, 6923412.0], [775403.0, 6934852.0], [777906.0, 6941851.0], [774574.0, 6946610.0], [779463.0, 6948255.0], [781387.0, 6953785.0], [790134.0, 6962730.0], [787172.0, 6965431.0], [789845.0, 6973793.0], [788558.0, 6985051.0], [781905.0, 6987282.0], [778060.0, 6986162.0], [770359.0, 6988977.0], [766237.0, 6992385.0], [753505.0, 6995276.0], [751253.0, 6997000.0], [744014.0, 6992056.0], [739058.0, 6995179.0], [735248.0, 6991264.0], [725313.0, 6993104.0], [720100.0, 6990781.0], [716534.0, 6992565.0], [712391.0, 6990404.0], [713833.0, 6986563.0], [708480.0, 6979518.0], [705667.0, 6969289.0], [708546.0, 6956332.0], [707064.0, 6950845.0], [709520.0, 6938240.0], [706939.0, 6934901.0], [711648.0, 6928031.0], [706805.0, 6926038.0], [706929.0, 6919738.0], [698137.0, 6911415.0], [701957.0, 6908433.0], [704672.0, 6899225.0], [710189.0, 6894765.0], [705248.0, 6890863.0], [712067.0, 6888882.0], [712559.0, 6879371.0], [722321.0, 6872132.0], [724211.0, 6867685.0], [729581.0, 6862815.0], [735603.0, 6861428.0], [738742.0, 6868146.0], [744067.0, 6871735.0], [747254.0, 6882494.0], [743801.0, 6891376.0], [745398.0, 6894771.0], [751361.0, 6898188.0], [747051.0, 6913033.0], [761575.0, 6918670.0], [767112.0, 6923360.0], [775242.0, 6918312.0], [776081.0, 6923412.0]]]}}, 2: {'attributes': {'CODE_DEPT': '95', 'NOM_DEPT': "VAL-D'OISE"}, 'geometry': {'type': 'Polygon', 'coordinates': [[[598361.0, 6887345.0], [603102.0, 6887292.0], [606678.0, 6883543.0], [614076.0, 6886919.0], [622312.0, 6880731.0], [628641.0, 6878089.0], [633062.0, 6879807.0], [641836.0, 6872490.0], [641404.0, 6867928.0], [648071.0, 6872567.0], [653619.0, 6875101.0], [660416.0, 6872923.0], [667303.0, 6878971.0], [670084.0, 6886723.0], [659205.0, 6894147.0], [652314.0, 6895981.0], [649761.0, 6898738.0], [645465.0, 6895048.0], [633020.0, 6901508.0], [626847.0, 6897876.0], [618689.0, 6896449.0], [612180.0, 6899061.0], [608283.0, 6898554.0], [605624.0, 6904387.0], [603501.0, 6902160.0], [601892.0, 6893098.0], [598361.0, 6887345.0]]]}}, 3: {'attributes': {'CODE_DEPT': '56', 'NOM_DEPT': 'MORBIHAN'}, 'geometry': {'type': 'Polygon', 'coordinates': [[[229520.0, 6710085.0], [240383.0, 6704696.0], [240163.0, 6708285.0], [235835.0, 6713741.0], [229006.0, 6716339.0], [229520.0, 6710085.0]]]}}, 4: {'attributes': {'CODE_DEPT': '56', 'NOM_DEPT': 'MORBIHAN'}, 'geometry': {'type': 'Polygon', 'coordinates': [[[212687.0, 6770001.0], [211559.0, 6762660.0], [216528.0, 6752538.0], [224759.0, 6753321.0], [234540.0, 6747533.0], [234220.0, 6745025.0], [240082.0, 6736634.0], [251238.0, 6736509.0], [260889.0, 6740570.0], [266327.0, 6740184.0], [271833.0, 6736526.0], [269308.0, 6731426.0], [263161.0, 6733044.0], [258643.0, 6731063.0], [263631.0, 6725691.0], [274085.0, 6728424.0], [283689.0, 6728526.0], [290663.0, 6724762.0], [288997.0, 6719519.0], [300067.0, 6720583.0], [315995.0, 6726944.0], [317487.0, 6738014.0], [315562.0, 6748257.0], [318803.0, 6749864.0], [322365.0, 6758359.0], [317839.0, 6765781.0], [320890.0, 6769878.0], [317014.0, 6776765.0], [309516.0, 6779524.0], [306739.0, 6782705.0], [310549.0, 6787938.0], [306966.0, 6794650.0], [300637.0, 6793781.0], [298204.0, 6799128.0], [291749.0, 6798375.0], [285132.0, 6789099.0], [280665.0, 6785525.0], [277875.0, 6787107.0], [279762.0, 6794931.0], [270150.0, 6795768.0], [252150.0, 6805897.0], [246074.0, 6807146.0], [242780.0, 6802066.0], [233945.0, 6800703.0], [229439.0, 6804532.0], [212675.0, 6807535.0], [202658.0, 6804638.0], [202166.0, 6798131.0], [205220.0, 6785800.0], [211608.0, 6786141.0], [216607.0, 6782805.0], [223352.0, 6780867.0], [221788.0, 6771592.0], [212687.0, 6770001.0]]]}}}},
    },
}


def test_all():
    # create_geolayer_from_i_feat_list
    print(
        test_function(
            create_geolayer_from_i_feat_list,
            create_geolayer_from_i_feat_list_parameters,
        )
    )

    # reproject_geolayer
    print(test_function(reproject_geolayer, reproject_geolayer_parameters))

    # multi_geometry_to_single_geometry_geolayer
    print(
        test_function(
            multi_geometry_to_single_geometry_geolayer,
            multi_geometry_to_single_geometry_geolayer_parameters,
        )
    )

    # geolayer_to_2d_geolayer
    print(test_function(geolayer_to_2d_geolayer, geolayer_to_2d_geolayer_parameters))


if __name__ == "__main__":
    test_all()
