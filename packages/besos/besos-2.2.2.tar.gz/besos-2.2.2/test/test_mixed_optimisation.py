import random

import pytest

from besos import optimizer
from besos.evaluator import EvaluatorGeneric
from besos.parameters import CategoryParameter, Parameter, RangeParameter
from besos.problem import Problem


@pytest.fixture
def parameters():
    parameters = [
        Parameter(value_descriptors=CategoryParameter(list(range(80, 90)), name="1st")),
        Parameter(value_descriptors=CategoryParameter(list(range(80, 90)), name="2nd")),
        Parameter(value_descriptors=RangeParameter(3, 100, name="3rd")),
    ]
    return parameters


def mixed_types(values):
    # helper function from the jupyter notebook
    values = list(values)
    num = values.pop(-1)
    return tuple(num % v for v in values)


def test_mixed_type_parameters(parameters, regtest):
    """to make sure that we can use different parameter types in the same algorithms
    while still getting optimal outputs"""

    evaluator = EvaluatorGeneric(mixed_types, Problem(parameters, 2))
    random.seed(1)
    results = optimizer.EpsMOEA(evaluator, epsilons=10)

    results = results[["outputs_0", "outputs_1"]].values[0]
    with regtest:
        print([f"{x:.5E}" for x in results])


def test_optimizer_customization(parameters, regtest):
    """testing the variator field while using mixed parameters"""

    evaluator = EvaluatorGeneric(mixed_types, Problem(parameters, 2))
    variator = optimizer.get_operator(evaluator.to_platypus())

    random.seed(2)
    results = optimizer.EpsMOEA(evaluator, variator=variator, epsilons=10)

    results = results[["outputs_0", "outputs_1"]].values[0]
    with regtest:
        print([f"{x:.5E}" for x in results])
