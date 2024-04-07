from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn import linear_model, pipeline
from sklearn.preprocessing import StandardScaler

from besos import config
from besos import eplus_funcs
from besos import eppy_funcs as ef
from besos import sampling
from besos.evaluator import EvaluatorEP
from besos.parameters import FieldSelector, Parameter, RangeParameter
from besos.problem import EPProblem


# Some code taken and adapted from example notebooks, made to work through pytest


@pytest.fixture
def building():
    return ef.get_building()


@pytest.fixture
def unexpanded():
    return ef.get_building(str(Path(config.data_dir, "unexpanded.idf").resolve()))


@pytest.fixture
def parameters():
    parameters = [
        Parameter(
            FieldSelector(
                object_name="NonRes Fixed Assembly Window",
                field_name="Solar Heat Gain Coefficient",
            ),
            value_descriptors=RangeParameter(0.01, 0.99),
        ),
        Parameter(
            FieldSelector("Lights", "*", "Watts per Zone Floor Area"),
            value_descriptors=RangeParameter(8, 12, name="Lights Watts/Area"),
        ),
    ]
    return parameters


@pytest.fixture
def problem(parameters):
    objectives = ["Electricity:Facility"]
    problem = EPProblem(parameters, objectives)
    return problem


@pytest.fixture
def samples(problem):
    samples = sampling.dist_sampler(sampling.seeded_sampler, problem, 10)
    return samples


@pytest.mark.slow
def test_expected_values(building, problem, samples, regtest):
    """check that the obtained results are consistent when using the same inputs"""

    def get_plot_data(model, density):
        # helper function from the example notebook
        d1 = problem.value_descriptors[0]
        a = np.linspace(d1.min, d1.max, density)
        d2 = problem.value_descriptors[1]
        b = np.linspace(d2.min, d2.max, density)
        plot_data = pd.DataFrame(
            np.transpose([np.tile(a, len(b)), np.repeat(b, len(a))]),
            columns=problem.names("inputs"),
        )
        return pd.concat([plot_data, pd.Series(model.predict(plot_data))], axis=1)

    evaluator = EvaluatorEP(problem, building, error_mode="Silent")
    train = evaluator.df_apply(samples, keep_input=True)
    print(problem.names())
    x, y, c = problem.names()

    # train and get the values
    model = pipeline.make_pipeline(StandardScaler(), linear_model.Ridge())
    model.fit(train[[x, y]].values, train[c].values)
    density = 30
    df = get_plot_data(model, int(density * 1.5))

    # check to see if the extremes and the midpoint are the expected values
    with regtest:
        for index in [0, 1012, 2024]:
            print(f"{df.iloc[index][0]:.5E}")

    samples = sampling.dist_sampler(
        sampling.neighborhood_sample, problem, 1, problem_dup=problem
    )
    assert samples.shape == (5, 2)
    assert 0.01 == samples.iloc[1, 0]
    assert 0.99 == samples.iloc[2, 0]
    assert 8.0 == samples.iloc[3, 1]
    assert 12.0 == samples.iloc[4, 1]
    assert samples.iloc[0, 0] == samples.iloc[3, 0] == samples.iloc[4, 0]
    assert samples.iloc[0, 1] == samples.iloc[1, 1] == samples.iloc[2, 1]

    samples = sampling.dist_sampler(
        sampling.morris_sample, problem, 1, problem_dup=problem
    )
    assert samples.shape == (3, 2)
    assert samples.iloc[0, 1] == samples.iloc[1, 1]
    assert samples.iloc[1, 0] == samples.iloc[2, 0]
    assert samples.iloc[0, 0] != samples.iloc[1, 0]
    assert samples.iloc[1, 1] != samples.iloc[2, 1]


@pytest.mark.slow
def test_expand_objects_run(unexpanded):
    eplus_funcs.run_building(unexpanded, err_dir=config.err_dir / "BESOS_Errors")
