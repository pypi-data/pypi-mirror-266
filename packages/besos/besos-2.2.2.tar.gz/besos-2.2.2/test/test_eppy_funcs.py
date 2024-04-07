from io import BytesIO
from pathlib import Path
import warnings

from eppy.modeleditor import IDDAlreadySetError
import pytest

from besos import config
from besos import eplus_funcs
from besos import eppy_funcs as ef


@pytest.fixture(params=["idf", "json"])
def building(request):
    return ef.get_building(mode=request.param)


@pytest.fixture
def clean_idd_name():
    # reset the iddname
    # this kind of monkeypatch should not be used in production
    # it may mess with how idfs are processed

    # clear name before test
    old_name = ef.IDF.iddname
    ef.IDF.iddname = None
    yield
    # restore name after test
    ef.IDF.iddname = old_name


@pytest.fixture
def idd_other(clean_idd_name):
    return Path(config.data_dir, "Custom_Long_Fields.idd")


def test_idd_no_conflict_defaults(clean_idd_name):
    ef.get_idf()
    ef.get_idf()


def test_idd_no_conflict_same(idd_other, clean_idd_name):
    ef.get_idf(idd_file=idd_other)
    ef.get_idf(idd_file=idd_other)


def test_idd_conflict(idd_other, clean_idd_name):
    with pytest.raises(IDDAlreadySetError):
        ef.get_idf()
        ef.get_idf(idd_file=idd_other)


def test_idd_warns(idd_other, clean_idd_name):
    ef.get_idf(idd_file=idd_other)
    with pytest.warns(UserWarning, match="idd is already set to: "):
        ef.get_idf()


# def test_view_building(building, regtest):
#     """Verify that the view building function gives consistent results."""
#     fig, ax = ef.view_building(building)
#     out = BytesIO()
#     fig.savefig(out)
#     with regtest:
#         print(out.getvalue())


def test_remove_shading():
    building = ef.get_building(mode="idf")
    building.add_overhangs(
        0.3
    )  # NOTE: Floats are completely arbitrary and can be edited
    building.remove_shading()
    assert building.getshadingsurfaces() == []


def test_remove_windows():
    building = ef.get_building(mode="idf")
    building.remove_windows()
    assert (
        len(building.idfobjects["FENESTRATIONSURFACE:DETAILED"]) == 0
    )  # test relies on all FENESTRATIONSURFACE:DETAILED objects being windows


def test_wwr_all(building, regtest):
    with warnings.catch_warnings():
        warnings.simplefilter(
            "ignore", category=UserWarning
        )  # ignores glassdoor warning
        ef.wwr_all(
            building, 0.235
        )  # NOTE: Floats and directions are completely arbitrary and can be edited
        no_direction = ef.get_windows(building)
        ef.wwr_all(building, 0.5, direction="north")
        with_direction = ef.get_windows(building)
    with regtest:
        print(no_direction)
        print(with_direction)


def test_set_daylight_control(regtest):
    building = ef.get_building(mode="idf")
    ef.set_daylight_control(building, zone_name="Perimeter_ZN_1", distance=2)
    with regtest:
        print(building.idfobjects["Daylighting:Controls"])
