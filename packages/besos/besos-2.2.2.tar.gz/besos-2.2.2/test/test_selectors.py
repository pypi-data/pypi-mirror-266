import pytest

from besos import eppy_funcs as ef
from besos.errors import ModeError
from besos.parameters import (
    FieldSelector,
    FilterSelector,
    GenericSelector,
)


@pytest.fixture
def json_building():
    return ef.get_building(mode="json")


@pytest.fixture
def idf_building():
    return ef.get_building(mode="idf")


@pytest.fixture(params=["json", "idf"])
def building(request):
    return ef.get_building(mode=request.param)


@pytest.fixture
def filter_selector():
    def insulation_filter(building):
        mode = ef.get_mode(building)
        if mode == "idf":
            return [
                obj
                for obj in building.idfobjects["MATERIAL"]
                if "Insulation" in obj.Name
            ]
        elif mode == "json":
            return [
                obj
                for name, obj in building["Material"].items()
                if "Insulation" in name
            ]
        else:
            raise ModeError(mode)

    return FilterSelector(insulation_filter, "Thickness")


@pytest.fixture
def single_selector():
    return FieldSelector(
        class_name="Lights",
        object_name="Core_ZN_Lights",
        field_name="Watts per Zone Floor Area",
    )


@pytest.fixture
def intuited_selector():
    return FieldSelector(
        # class_name omitted
        object_name="1/2IN Gypsum",
        field_name="Conductivity",
    )


@pytest.fixture
def star_selector():
    return FieldSelector(
        class_name="Lights", object_name="*", field_name="Watts per Zone Floor Area"
    )


@pytest.fixture(
    params=["single_selector", "intuited_selector", "star_selector", "filter_selector"]
)
def selector(request):
    return request.getfixturevalue(request.param)


@pytest.fixture
def value():
    return 0.42


def test_init():
    """to make sure each type of selector is created as expected"""

    def insulation_filter(building):
        return [
            obj for name, obj in building["Material"].items() if "Insulation" in name
        ]

    field_selector = FieldSelector(
        class_name="Material",
        object_name="Mass NonRes Wall Insulation",
        field_name="Thickness",
    )
    filter_selector = FilterSelector(insulation_filter, "Thickness")
    generic_selector = GenericSelector(set=ef.wwr_all, setup=ef.one_window)

    # basic checks for the expected output format
    assert (
        str(field_selector)
        == "FieldSelector(field_name='Thickness', class_name='Material', "
        "object_name='Mass NonRes Wall Insulation')"
    ), f"FieldSelector not properly initialised: {field_selector}"
    assert (
        filter_selector.field_name == "Thickness"
        and str(type(filter_selector.get_objects)) == "<class 'method'>"
    ), f"FilterSelector not properly initialised: {filter_selector}"
    assert (
        str(type(generic_selector.set)) == "<class 'method'>"
        and str(type(generic_selector.setup)) == "<class 'method'>"
    ), f"GenericSelector not properly initialised: {generic_selector}"


def test_set_matches_get(building, selector, value):
    """Verifies that after setting a value with a selector, get returns the same value"""

    selector.set(building, value)

    assert set(selector.get(building)) == {
        value
    }, "Wrong value retrieved by get operation"


def test_idf_filter_selector(idf_building, filter_selector, value):
    building = idf_building
    filter_ = filter_selector

    found_objects = [obj.Name for obj in filter_.get_objects(building)]
    correct_objects = [
        "Mass NonRes Wall Insulation",
        "AtticFloor NonRes Insulation",
    ]

    assert (
        found_objects == correct_objects
    ), f"filter found {found_objects}, should have found {correct_objects}"

    filter_.set(building, value)
    assert (
        building.idfobjects["MATERIAL"][0].Thickness == value
    ), "Value set incorrectly"

    assert filter_.get(building) == [
        value,
        value,
    ], "Wrong value retrieved by get operation"


def test_json_filter_selector(json_building, filter_selector, value):
    building = json_building
    filter_ = filter_selector
    found_objects = filter_.get_objects(building)
    correct_objects = [
        building["Material"]["Mass NonRes Wall Insulation"],
        building["Material"]["AtticFloor NonRes Insulation"],
    ]
    assert (found_objects == correct_objects) or (
        found_objects == correct_objects[::-1]
    ), f"filter found {found_objects}, should have found {correct_objects}"

    filter_.set(building, value)

    assert (
        building["Material"]["AtticFloor NonRes Insulation"]["thickness"] == value
    ), "Value set incorrectly"
