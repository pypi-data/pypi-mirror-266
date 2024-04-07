import shutil

import numpy as np
import pytest

from besos.evaluator import EvaluatorGeneric
from besos.optimizer import rbf_opt
from besos.parameters import Parameter, RangeParameter
from besos.problem import Problem


@pytest.mark.skipif(shutil.which("bonmin") is None, reason="Requires bonmin to run.")
def test_rbfopt():
    """Simple test to make sure RBFOpt can be run properly"""

    def objective_function(x):
        return (x[0] * x[1] - x[2],)

    param_list = [Parameter(value_descriptors=RangeParameter(0, 10)) for _ in range(3)]
    problem = Problem(param_list, 1)

    evaluator = EvaluatorGeneric(objective_function, problem, error_mode="Silent")

    opt = rbf_opt(evaluator, 30)
    value = opt.iloc[0]

    print(opt)

    assert (
        np.isclose(value["RangeParameter [0, 10]"], 0)
        and (
            np.isclose(value["RangeParameter [0, 10]_1"], 5.062882681226724)
            or np.isclose(value["RangeParameter [0, 10]_1"], 0.5148690)
        )
        and np.isclose(value["RangeParameter [0, 10]_2"], 10)
        and np.isclose(value["outputs_0"], -10)
    ), f"Unexpected output: {value}"  # None_1 assert values hardcoded to pass on Debian
