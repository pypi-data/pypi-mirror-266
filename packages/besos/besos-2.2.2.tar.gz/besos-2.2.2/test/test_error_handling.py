import subprocess

import numpy as np
import pytest

from besos import config
from besos import eppy_funcs as ef
from besos import sampling
from besos.evaluator import EvaluatorEP, EvaluatorGeneric
from besos.parameters import CategoryParameter, FieldSelector, Parameter, RangeParameter
from besos.problem import EPProblem, Problem


@pytest.fixture
def building():
    return ef.get_building()


@pytest.fixture
def problem():
    problem = EPProblem(
        [
            Parameter(
                FieldSelector(
                    object_name="Mass NonRes Wall Insulation", field_name="Thickness"
                ),
                RangeParameter(min_val=0.01, max_val=0.99),
            ),
            Parameter(
                FieldSelector(
                    class_name="Construction",
                    object_name="ext-slab",
                    field_name="Outside Layer",
                ),
                CategoryParameter(options=("HW CONCRETE", "Invalid Material")),
            ),
        ]
    )
    return problem


@pytest.fixture
def samples(problem):
    # seeded_sampler results in indexes 0-3 being Invalid Material and 4 being HW
    # CONCRETE
    samples = sampling.dist_sampler(sampling.seeded_sampler, problem, 5)
    return samples


def test_exception_throwing(building, problem, samples):
    """test to make sure exceptions are thrown in Failfast mode"""

    # check that an exception is raised with FailFast mode
    with pytest.raises(subprocess.CalledProcessError), pytest.warns(
        UserWarning, match="problematic values were:"
    ):
        EvaluatorEP(problem, building, error_mode="Failfast").df_apply(samples)


def test_exception_warn(building, problem, samples):
    # check that no exceptions are raised in the other mode
    with pytest.warns(UserWarning, match="problematic values were:"):
        EvaluatorEP(problem, building, error_mode="Print").df_apply(samples)


@pytest.mark.slow
def test_exception_silent(building, problem, samples):
    # check that no exceptions are raised in the other mode
    EvaluatorEP(problem, building, error_mode="Silent").df_apply(samples)


def test_error_bad_idf(problem):
    """To make sure EvaluatorEP error handling works"""
    building = ef.get_building(config.files.get("bad_idf"))
    evaluator = EvaluatorEP(problem, building)
    with pytest.raises(subprocess.CalledProcessError), pytest.warns(
        UserWarning, match="problematic values were:"
    ):
        evaluator([0.5, "HW CONCRETE"])


@pytest.fixture
def error_on_invalid():
    def f(values):
        print(values)
        if values[1] == "Invalid Material":
            print("invalid")
            raise ValueError
        else:
            return (1,)

    return f


def test_error_values(error_on_invalid, problem, samples):
    """check that automatic error handling will assign the desired error values"""

    # check that the default error value is assigned to invalid materials
    evaluator = EvaluatorGeneric(error_on_invalid, problem, error_mode="Silent")
    results = evaluator.df_apply(samples)
    value = results.iloc[0]["Electricity:Facility"]
    assert value == np.inf, (
        f"Invalid material not assigned the default error value, value assigned was: "
        f"{value}"
    )

    # check that a custom error value is assigned to invalid materials
    error_value = (-1,)
    evaluator = EvaluatorGeneric(
        error_on_invalid, problem, error_mode="Silent", error_value=error_value
    )
    results = evaluator.df_apply(samples)
    value = results.iloc[0]["Electricity:Facility"]
    assert value == -1, (
        f"Invalid material not assigned the correct error value, value assigned wa"
        f"s: {value}"
    )

    # check that valid inputs aren't assigned error values
    value = results.iloc[4]["Electricity:Facility"]
    assert value != -1, f"Valid material was assigned the error value: {error_value}"


@pytest.fixture
def error_value_tester():
    def helper(problem, error_value, **kwargs):
        return EvaluatorGeneric(
            lambda x: (1 / 0),
            problem,
            error_value=error_value,
            error_mode="Silent",
            **kwargs,
        )([])

    return helper


@pytest.mark.parametrize(
    "outputs, constraints, error_value, answer",
    [
        (0, 0, None, ()),
        (1, 0, None, (float("inf"),)),
        (
            2,
            0,
            None,
            (float("inf"), float("inf")),
        ),
        (
            2,
            0,
            (None, None),
            (float("inf"), float("inf")),
        ),
    ],
)
def test_error_objectives_both_versions(
    error_value_tester, outputs, constraints, error_value, answer
):
    """These tests should pass with both the new and the old error_value handling"""
    assert error_value_tester(
        Problem(
            0,
            outputs,
            constraints,
            constraint_bounds=["dummy value"] * constraints,
        ),
        error_value=error_value,
    ) == list(answer)


@pytest.mark.compatibility
@pytest.mark.parametrize(
    "outputs, constraints, error_value, answer",
    [
        (0, 0, (None, None), ()),
        (1, 0, (None, None), (float("inf"),)),
        (
            3,
            0,
            (None, None),
            (
                float("inf"),
                float("inf"),
                float("inf"),
            ),
        ),
        (
            1,
            0,
            ((1,), ()),
            (1,),
        ),
        (
            2,
            0,
            ((1, 2), ()),
            (1, 2),
        ),
        (
            1,
            0,
            ((1,), None),
            (1,),
        ),
        (
            2,
            0,
            ((1, 2), None),
            (1, 2),
        ),
        (
            0,
            2,
            ((), (1, 2)),
            (1, 2),
        ),
        (
            0,
            2,
            (None, (1, 2)),
            (1, 2),
        ),
        (
            1,
            1,
            ((1,), (2,)),
            (1, 2),
        ),
        (
            1,
            1,
            (None, (1,)),
            (float("inf"), 1),
        ),
    ],
)
def test_error_objectives(
    error_value_tester, outputs, constraints, error_value, answer
):
    with pytest.warns(
        FutureWarning, match="Evaluators have changed the format used for error values."
    ):
        assert error_value_tester(
            Problem(
                0,
                outputs,
                constraints,
                constraint_bounds=["dummy value"] * constraints,
            ),
            error_value=error_value,
        ) == list(answer)
