import numpy as np
import pytest
from sklearn import linear_model
from sklearn.model_selection import train_test_split

from besos import eppy_funcs as ef
from besos import optimizer
from besos import sampling
from besos.evaluator import EvaluatorEP, EvaluatorGeneric
from besos.parameters import expand_plist
from besos.problem import EPProblem


@pytest.fixture
def building():
    return ef.get_building()


@pytest.fixture
def problem():
    parameters = expand_plist(
        {
            "Mass NonRes Wall Insulation": {"Thickness": (0.01, 0.99)},
            "NonRes Fixed Assembly Window": {
                "U-Factor": (0.1, 5),
                "Solar Heat Gain Coefficient": (0.01, 0.99),
            },
        }
    )
    return EPProblem(parameters, ["Electricity:Facility"])


@pytest.fixture
def samples(problem):
    return sampling.dist_sampler(sampling.seeded_sampler, problem, 10)


@pytest.mark.slow
def test_fit(building, problem, samples):
    """check to make sure linear regression works and is close to the actual value"""

    evaluator = EvaluatorEP(problem, building)
    outputs = evaluator.df_apply(samples)

    train_in, test_in, train_out, test_out = train_test_split(
        samples, outputs, test_size=0.2
    )

    reg = linear_model.LinearRegression()
    reg.fit(train_in, train_out)
    results = test_in.copy()
    results["energy use"] = test_out
    results["predicted"] = reg.predict(test_in)

    actual = results.iloc[0]["energy use"]
    predicted = results.iloc[0]["predicted"]
    assert np.isclose(
        actual - predicted, 8666133.340038776
    ), f"Unexpected difference of value: {actual - predicted}"


@pytest.mark.slow
def test_optimisation_with_surrogate(building, problem, samples):
    """make sure we can run optimisation algorithms on the fit surrogates"""

    evaluator = EvaluatorEP(problem, building)
    outputs = evaluator.df_apply(samples)

    train_in, test_in, train_out, test_out = train_test_split(
        samples, outputs, test_size=0.2
    )

    reg = linear_model.LinearRegression()
    reg.fit(train_in, train_out)

    def evaluation_func(ind):
        return (reg.predict([ind])[0][0],)

    surrogate = EvaluatorGeneric(evaluation_func, problem)

    s = optimizer.NSGAII(surrogate, 1000)

    optimal = s.iloc[0]["pareto-optimal"]
    non_optimal = s.iloc[1]["pareto-optimal"]

    assert optimal, f"Optimal output was displayed as not Pareto Optimal"
    assert not non_optimal, f"Non-optimal output was displayed as Pareto Optimal"
