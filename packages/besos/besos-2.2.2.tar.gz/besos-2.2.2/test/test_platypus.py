import random
import shutil

import platypus
import pytest

from besos import eppy_funcs as ef
from besos import optimizer
from besos import pyehub_funcs as pf
from besos.evaluator import EvaluatorEP, EvaluatorEH
from besos.parameters import (
    Parameter,
    RangeParameter,
    PathSelector,
    expand_plist,
)
from problem import EPProblem, EHProblem


needs_glpk = pytest.mark.skipif(
    shutil.which("glpsol") is None,
    reason=("Requires a PuLP compatible solver. Tests assume GLPK is the solver used."),
)


@pytest.fixture
def parameters():
    parameters = expand_plist(
        {
            "NonRes Fixed Assembly Window": {
                "UFactor": (0.1, 5),
                "Solar Heat Gain Coefficient": (0.01, 0.99),
            },
            "Mass NonRes Wall Insulation": {"Thickness": (0.01, 0.09)},
        }
    )
    return parameters


@pytest.fixture
def EHparameters():
    parameters = [
        Parameter(
            PathSelector(["LINEAR_CAPITAL_COSTS", "Boiler"]),
            value_descriptors=RangeParameter(100.0, 200.0, name="Boiler"),
        ),
        Parameter(
            PathSelector(["LINEAR_CAPITAL_COSTS", "CHP"]),
            value_descriptors=RangeParameter(300.0, 400.0, name="CHP"),
        ),
    ]
    return parameters


@pytest.fixture
def EHproblem(EHparameters):
    objectives = ["total_cost", "total_carbon"]
    return EHProblem(EHparameters, objectives)


@pytest.fixture
def problem(parameters):
    objectives = ["Electricity:Facility", "Gas:Facility"]
    return EPProblem(parameters, objectives)


@pytest.mark.slow
def test_flexibility(problem, regtest):
    """to make sure that you can use multiple algorithms on the same data set"""
    idf = ef.get_idf()
    evaluator = EvaluatorEP(problem, idf)

    random.seed(1)
    # run the first algorithm
    platypus_problem = evaluator.to_platypus()
    algorithm = platypus.NSGAII(problem=platypus_problem, population_size=5)
    algorithm.run(5)

    # run the second algorithm
    generator = platypus.InjectedPopulation(algorithm.population)
    alg2 = platypus.EpsMOEA(
        problem=platypus_problem, generator=generator, epsilons=3, population_size=5
    )
    alg2.run(5)

    results = optimizer.solutions_to_df(
        alg2.result, problem, parts=["inputs", "outputs"]
    )

    value = results.iloc[0]["Electricity:Facility"]
    with regtest:
        print(f"{value:.5E}")
    assert all(
        [optimal for optimal in results["pareto-optimal"]]
    ), f"Algorithm not producing optimal outputs"


@needs_glpk
@pytest.mark.slow
def test_energyhub(EHproblem):
    hub = pf.get_hub()
    evaluatorEH = EvaluatorEH(EHproblem, hub)
    platypus_problem = evaluatorEH.to_platypus()
    EHalgorithm = platypus.NSGAII(platypus_problem)
    EHalgorithm.run(5)
    results1 = optimizer.solutions_to_df(
        EHalgorithm.result, EHproblem, parts=["inputs", "outputs"]
    )
    best = results1.loc[results1["pareto-optimal"]]
    value = best.iloc[0]["total_cost"]

    assert value < 1000, f"Unexpected result: {value}"
