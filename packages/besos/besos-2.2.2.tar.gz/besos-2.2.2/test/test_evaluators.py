import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from unittest import mock as mocker

from besos import config
from besos import eppy_funcs as ef
from besos import pyehub_funcs as pf
from besos import sampling
from besos.evaluator import EvaluatorEH, EvaluatorEP, EvaluatorGeneric
from besos.parameters import (
    FieldSelector,
    Parameter,
    ParameterEH,
    PathSelector,
    RangeParameter,
)
from besos.problem import EHProblem, EPProblem, Problem


needs_glpk = pytest.mark.skipif(
    shutil.which("glpsol") is None,
    reason=("Requires a PuLP compatible solver. Tests assume GLPK is the solver used."),
)


@pytest.fixture
def building():
    # returns the basic building
    return ef.get_building()


@pytest.fixture
def unexpanded():
    return ef.get_building(str(Path(config.data_dir, "unexpanded.idf")))


@pytest.fixture
def hub():
    # returns the basic hub
    return pf.get_hub()


@pytest.fixture
def problem():
    parameters = [
        Parameter(
            FieldSelector(
                object_name="Mass NonRes Wall Insulation", field_name="Thickness"
            )
        )
    ]
    objectives = [
        "Electricity:Facility",
        "Gas:Facility",
    ]  # the default is just 'Electricity:Facility'

    return EPProblem(parameters, objectives)


@pytest.fixture()
def sample_ready_problem():
    parameters = [
        Parameter(
            FieldSelector(
                object_name="Mass NonRes Wall Insulation", field_name="Thickness"
            ),
            RangeParameter(0.1, 0.9),
        )
    ]
    objectives = [
        "Electricity:Facility",
        "Gas:Facility",
    ]  # the default is just 'Electricity:Facility'

    return EPProblem(parameters, objectives)


@pytest.fixture()
def inputs(sample_ready_problem):
    return sampling.dist_sampler(sampling.lhs, sample_ready_problem, 2)


@pytest.fixture
def energyhub_df():
    return pd.DataFrame(np.array([[200, 600], [600, 200]]), columns=["p1", "p2"])


@pytest.fixture
def energyplus_df():
    return pd.DataFrame(np.array([[0.5], [0.8]]), columns=["p1"])


@pytest.fixture
def hub_problem():

    parameters = [
        Parameter(PathSelector(["LINEAR_CAPITAL_COSTS", "Boiler"])),
        Parameter(PathSelector(["LINEAR_CAPITAL_COSTS", "CHP"])),
    ]
    objectives = ["total_cost", "total_carbon"]

    return EHProblem(parameters, objectives)


# @pytest.fixture
# def oldstyle_hub_problem():
#     parameters = []
#     message = (
#         "Use a :class:`PathSelector` and a :class:`Parameter` instead. "
#         "These have been swapped in automatically."
#     )
#     with pytest.warns(DeprecationWarning, match=message):
#         parameters.append(ParameterEH(["LINEAR_CAPITAL_COSTS", "Boiler"]))
#     with pytest.warns(DeprecationWarning, match=message):
#         parameters.append(ParameterEH(["LINEAR_CAPITAL_COSTS", "CHP"]))
#     objectives = ["total_cost", "total_carbon"]

#     return EHProblem(parameters, objectives)


# @needs_glpk
# @pytest.mark.compatibility
# def test_equivalent_problems(hub_problem, oldstyle_hub_problem, hub):
#     evaluator_new = EvaluatorEH(hub_problem, hub)
#     evaluator_old = EvaluatorEH(oldstyle_hub_problem, hub)
#     result_new = evaluator_new([200, 600])
#     result_old = evaluator_old([200, 600])
#     assert np.allclose(
#         result_new, result_old
#     ), "Hub compatibility transformation does not work"


@pytest.mark.slow
def test_evaluatorEP(building, problem, regtest):
    """To make sure EvaluatorEP can be initialised and works as intended"""

    evaluator = EvaluatorEP(problem, building)
    result = evaluator([0.5])  # run with thickness set to 0.5

    with regtest:
        print([f"{x:.5E}" for x in result])


@needs_glpk
def test_evaluatorEH_single(hub, hub_problem, regtest):
    """To make sure EvaluatorEH can be initialised and works as intended"""

    evaluator = EvaluatorEH(hub_problem, hub)
    result = evaluator([200, 600])

    with regtest:
        print([f"{x:.5E}" for x in result])


@needs_glpk
def test_evaluatorEH_df(hub, hub_problem, energyhub_df, regtest):
    """To make sure EvaluatorEH df_apply works as intended"""

    evaluator = EvaluatorEH(hub_problem, hub)
    result = evaluator.df_apply(energyhub_df)

    with regtest:
        print(result)


@needs_glpk
@pytest.mark.slow
def test_evaluatorEH_EP(hub, hub_problem, building, problem, regtest):
    """To make sure that base EvaluatorEP output can be used in an EvaluatorEH"""
    evaluatorEP = EvaluatorEP(problem, building)
    evaluatorEH = EvaluatorEH(hub_problem, hub)
    result = evaluatorEH(evaluatorEP([0.5]))

    with regtest:
        print([f"{x:.5E}" for x in result])


@needs_glpk
def test_evaluatorEH_TS(hub, regtest):
    """To make sure that EvaluatorEH can accept a time series as input"""
    timeseries = [
        {
            0: 4.0,
            1: 8.0,
            2: 6.0,
            3: 5.0,
            4: 7.0,
            5: 7.0,
            6: 7.0,
            7: 7.0,
            8: 7.0,
            9: 7.0,
            10: 7.0,
        }
    ]

    time_series_parameters = [Parameter(PathSelector(["LOADS", "Elec"]))]

    objectives = ["total_cost", "total_carbon"]
    time_series_problem = EHProblem(time_series_parameters, objectives)
    evaluatorEH = EvaluatorEH(time_series_problem, hub)
    result = evaluatorEH(timeseries)

    with regtest:
        print([f"{x:.5E}" for x in result])


@needs_glpk
def test_evaluatorEH_TS_df(hub, regtest):
    """To make sure that EvaluatorEH's df_apply can accept a dataframe of time series as input"""
    default_timeseries = [
        {
            0: 1.0,
            1: 4.0,
            2: 4.0,
            3: 4.0,
            4: 4.0,
            5: 4.0,
            6: 4.0,
            7: 4.0,
            8: 4.0,
            9: 4.0,
            10: 4.0,
        },
        {
            0: 20.0,
            1: 20.0,
            2: 20.0,
            3: 20.0,
            4: 20.0,
            5: 20.0,
            6: 20.0,
            7: 12.0,
            8: 12.0,
            9: 12.0,
            10: 12.0,
        },
    ]
    just_modified_heat = [
        {
            0: 1.0,
            1: 4.0,
            2: 4.0,
            3: 4.0,
            4: 4.0,
            5: 4.0,
            6: 4.0,
            7: 4.0,
            8: 4.0,
            9: 4.0,
            10: 4.0,
        },
        {
            0: 18.0,
            1: 18.0,
            2: 18.0,
            3: 18.0,
            4: 18.0,
            5: 18.0,
            6: 18.0,
            7: 16.0,
            8: 16.0,
            9: 16.0,
            10: 16.0,
        },
    ]
    just_modified_elec = [
        {
            0: 4.0,
            1: 8.0,
            2: 6.0,
            3: 5.0,
            4: 7.0,
            5: 7.0,
            6: 7.0,
            7: 7.0,
            8: 7.0,
            9: 7.0,
            10: 7.0,
        },
        {
            0: 20.0,
            1: 20.0,
            2: 20.0,
            3: 20.0,
            4: 20.0,
            5: 20.0,
            6: 20.0,
            7: 12.0,
            8: 12.0,
            9: 12.0,
            10: 12.0,
        },
    ]
    modified_timeseries = [
        {
            0: 4.0,
            1: 8.0,
            2: 6.0,
            3: 5.0,
            4: 7.0,
            5: 7.0,
            6: 7.0,
            7: 7.0,
            8: 7.0,
            9: 7.0,
            10: 7.0,
        },
        {
            0: 18.0,
            1: 18.0,
            2: 18.0,
            3: 18.0,
            4: 18.0,
            5: 18.0,
            6: 18.0,
            7: 16.0,
            8: 16.0,
            9: 16.0,
            10: 16.0,
        },
    ]
    timeseries_df = pd.DataFrame(
        np.array(
            [
                default_timeseries,
                just_modified_heat,
                just_modified_elec,
                modified_timeseries,
            ]
        ),
        columns=["p1", "p2"],
    )

    TSDFparameters = [
        Parameter(PathSelector(["LOADS", "Elec"])),
        Parameter(PathSelector(["LOADS", "Heat"])),
    ]
    TSDFobjectives = ["total_cost", "total_carbon"]
    TSDFproblem = EHProblem(TSDFparameters, TSDFobjectives)

    evaluatorEH = EvaluatorEH(TSDFproblem, hub)
    result = evaluatorEH.df_apply(timeseries_df)

    with regtest:
        print(result)


@needs_glpk
@pytest.mark.slow
def test_evaluatorEH_EP_df(hub, hub_problem, building, problem, energyplus_df, regtest):
    """To make sure that dataframe EvaluatorEP output can be used in an EvaluatorEH"""
    evaluatorEP = EvaluatorEP(problem, building)
    evaluatorEH = EvaluatorEH(hub_problem, hub)
    result = evaluatorEH.df_apply(evaluatorEP.df_apply(energyplus_df))

    with regtest:
        print(result)


def test_evaluatorGeneric(problem):
    """To make sure EvaluatorGeneric can be initialised and works as intended"""

    def function(values):
        return (values[0], values[0] ** 2)

    # this denotes a problem which takes 1 input, produces 2 outputs and no constraints.
    # The placeholder parameters/objectives will be generated automatically.
    new_problem = Problem(1, 2, 0)

    evaluator_1 = EvaluatorGeneric(function, problem)
    evaluator_2 = EvaluatorGeneric(function, new_problem)
    result_1 = evaluator_1([4])
    result_2 = evaluator_2([4])

    assert result_1 == (
        4,
        16,
    ), f"Unexpected result for EvaluatorGeneric with EPProblem, {result_1}"
    assert result_2 == (
        4,
        16,
    ), f"Unexpected result for EvaluatorGeneric with custom problem, {result_2}"


@pytest.mark.slow
def test_parallel_evaluatorEP(building, problem, energyplus_df, regtest):
    """To make sure EvaluatorEP works with multiple processes"""

    evaluator = EvaluatorEP(problem, building)
    result = evaluator.df_apply(energyplus_df, processes=2, keep_input=True)

    with regtest:
        print(result)


@pytest.mark.slow
def test_error_evaluatorEP(problem):
    """To make sure EvaluatorEP error handling works"""
    building = ef.get_building(config.files.get("bad_idf"))
    evaluator = EvaluatorEP(problem, building)
    with pytest.raises(subprocess.CalledProcessError):
        with pytest.warns(UserWarning, match="problematic values were:"):
            evaluator([0.5])  # run with thickness set to 0.5


@pytest.mark.slow
def test_keep_output_evaluatorEP(building, sample_ready_problem, inputs, tmpdir):
    """Verify that the keep_output flag saves output in the correct location."""
    temp_path = tmpdir.mkdir("tmp")
    evaluator = EvaluatorEP(sample_ready_problem, building, out_dir=temp_path)
    df = evaluator.df_apply(inputs, keep_dirs=True)
    for dir_ in df["output_dir"]:
        # verify that the file exists and is readable
        with open(Path(dir_, "eplusout.dxf"), "r") as f:
            f.readline()


@pytest.fixture
def old_style_evaluation_function():
    def f(values):
        return (1.0, 2.0), ()

    return f


@pytest.mark.compatibility
def test_separate_outputs_and_constraints(old_style_evaluation_function):
    """Verify that we can still use the old evaluation function return format.

    Old format: (output1, output2, ...), (constraint1, constraint2, ...)
    New format: (output1, output2, ..., constraint1, constraint2, ...)

    """

    evaluator = EvaluatorGeneric(
        old_style_evaluation_function, Problem(inputs=1, outputs=2, constraints=0)
    )
    with pytest.warns(
        FutureWarning,
        match="Evaluators have changed the format used for storing outputs and constraints",
    ):
        assert evaluator([1]) == (1.0, 2.0)


@pytest.mark.compatibility
def test_epw_file_rename(building):
    """Verify that calls that use epw_file still work, but produce a warning."""
    with pytest.warns(FutureWarning, match="epw_file has been deprecated"):
        evaluator = EvaluatorEP(
            problem=Problem(), building=building, epw_file=config.files["epw"]
        )
    assert evaluator.epw == config.files["epw"]


@pytest.mark.compatibility
def test_epw_duplicate_values(building):
    """Verify that calls using both epw and epw_file are rejected."""
    with pytest.raises(ValueError, match="epw_file and epw cannot be used together"):
        EvaluatorEP(problem=Problem(), building=building, epw="a", epw_file="b")


@pytest.mark.slow
def test_expand_objects(unexpanded):
    EvaluatorEP(problem=Problem(), building=unexpanded)([])


# TODO add tests for cache/multiprocessing


def test_cache():
    func = mocker.Mock(return_value=[5])
    evaluator = EvaluatorGeneric(
        func, Problem([Parameter(value_descriptors=RangeParameter(0, 1))])
    )
    evaluator([1])
    # this call should hit the cache, and not the mocked evaluation function
    evaluator([1])
    func.assert_called_once()
