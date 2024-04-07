from io import BytesIO
from pathlib import Path

import pytest
import warnings

from besos import config
from besos import eplus_funcs as eplus
from besos import eppy_funcs as ef
from besos.errors import InstallationError


@pytest.fixture(params=["idf", "json"])
def building(request):
    return ef.get_building(mode=request.param)


def test_get_ep_path():
    # first test regular get_ep_path
    ep_exe, ep_path = eplus.get_ep_path("9.0")
    # test ep_path works
    eplus.get_ep_path("9.0", ep_path=ep_path)
    # test error handling
    try:
        eplus.get_ep_path("9.3", ep_path=ep_path)
        raise ValueError(
            "Error should have been thrown as ep_path did not match ep_version"
        )
    except InstallationError:
        pass
    try:
        eplus.get_ep_path("9.0", ep_path="nonExistingDir")
        raise ValueError("ep_path does not exist, should have raised error")
    except InstallationError:
        pass


def test_get_possible_outputs(building, regtest):
    # NOTE: test relies on same idf to output same possible outputs.
    # test will most likely fail when new idfs are placed in config
    with regtest:
        eplus.print_available_outputs(building, name="Electricity:Facility")
        eplus.print_available_outputs(building, frequency="Monthly")
