from geoformat.index.attributes.hash import create_attribute_index

from tests.data.geolayers import geolayer_fr_dept_population
from tests.data.index import (
    geolayer_fr_dept_population_CODE_DEPT_hash_index,
    geolayer_fr_dept_population_INSEE_REG_hash_index,
)

from tests.utils.tests_utils import test_function

create_attribute_index_parameters = {
    0: {
        "geolayer": geolayer_fr_dept_population,
        "field_name": "CODE_DEPT",
        "return_value": geolayer_fr_dept_population_CODE_DEPT_hash_index
    },
    1: {
        "geolayer": geolayer_fr_dept_population,
        "field_name": "INSEE_REG",
        "return_value": geolayer_fr_dept_population_INSEE_REG_hash_index
    }
}

def test_all():

    # create_attribute_index
    print(test_function(create_attribute_index, create_attribute_index_parameters))

if __name__ == '__main__':
    test_all()