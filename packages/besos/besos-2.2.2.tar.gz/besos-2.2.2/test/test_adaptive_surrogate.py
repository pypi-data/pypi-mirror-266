import pytest
from pyKriging.krige import kriging
import pyKriging

from besos import sampling
from besos.evaluator import AdaptiveSR, EvaluatorGeneric
from besos.parameters import Parameter, RangeParameter
from besos.problem import Problem


# Class taken directly from the notebook
class KirgingEval(AdaptiveSR):
    # The model cannot handle multiple objectives, so we check for this when initializing
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.problem.num_outputs != 1:
            raise ValueError("This model cannont handle multiobjective problems.")
        if self.problem.num_constraints != 0:
            raise ValueError("This model cannont handle constrained problems.")

    # pyKriging models are able to generate datapoints which will improve the model the most
    # **kwargs is included, since the model's function has some options which we may want to access
    # such as the ability to sample near the minimum, instead of near the point of greatest uncertainty
    def get_infill(self, num_datapoints, **kwargs):
        return self.model.infill(num_datapoints, **kwargs)

    # since pyKriging's model has an addPoint method, we will use it to update the model instead
    # of initialising a new one each time. We loop through all of the new datapoints
    # and add them one at a time, then retrain the inner model.
    # note that self.model.train is not the same as self.train
    def update_model(self, new_data, old_data=None) -> None:
        for index, *row in new_data.itertuples():
            inputs = row[: self.problem.num_inputs]
            output = row[-1]
            assert len(row) == self.problem.num_inputs + self.problem.num_outputs
            self.model.addPoint(inputs, output)
        self.model.train()

    # The infill function will work automatically, since we have defined get_infill and update_model

    # we initialize and store a kriging model on the stored training data, and then
    # run the internal model's train function.
    def train(self):
        self.model = kriging(self.data.values[:, :-1], self.data.values[:, -1])
        self.model.train()

    # this model expects a 2d array representing a batch of inputs, but we only want
    # to evaluate one input point at a time, so we wrap the inputs in a list before passing
    # them to the model
    def eval_single(self, values):
        return (self.model.predict(list(values)),), ()


@pytest.fixture
def problem():
    return Problem(
        [
            Parameter(value_descriptors=RangeParameter(0, 1, name="first")),
            Parameter(value_descriptors=RangeParameter(0, 1, name="second")),
        ],
        outputs=1,
    )


@pytest.fixture
def evaluation_function():
    return pyKriging.testfunctions().branin


@pytest.mark.slow
def test_init(problem, evaluation_function):
    """Testing the initialization and functionality of an adaptive surrogate model"""

    evaluator = EvaluatorGeneric(evaluation_func=evaluation_function, problem=problem)

    inputs = sampling.dist_sampler(sampling.seeded_sampler, problem, 10)
    inputs = sampling.add_extremes(inputs, problem)

    # using the custom class for our own model training
    k = KirgingEval(reference=evaluator)
    k.do_infill(inputs)
    k.model.train()
    k.infill(5)
