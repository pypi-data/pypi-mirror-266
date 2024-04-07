import pytest

from besos import eppy_funcs as ef
from besos import sampling
from besos.evaluator import EvaluatorGeneric
from besos.parameters import (
    CategoryParameter,
    FieldSelector,
    Parameter,
    RangeParameter,
    wwr,
)
from besos.problem import Problem


# parameter - selector & descriptor
# selector - FilterSelector FieldSelector GenericSelector
# descriptor - RangeParameter CategoryParameter

# init, setup_checks, and setup_changes were moved directly from Will's code in
# parameters.py


@pytest.fixture(params=["idf", "json"])
def building(request):
    return ef.get_building(mode=request.param)


def test_init():
    # inputs should be initialisable
    Parameter(
        FieldSelector(object_name="NonRes Fixed Assembly Window", field_name="UFactor"),
        value_descriptors=RangeParameter(min_val=0.1, max_val=5),
    )
    wwr()
    wwr(value_descriptor=RangeParameter(0.01, 0.99, name="other"))
    print("Parameters initialised")


def test_load_idf():
    idf = ef.get_idf()
    assert len(idf.idfobjects["FENESTRATIONSURFACE:DETAILED"]) == 21, "bad idf"


@pytest.mark.xfail
def test_setup_checks():
    # try excepts were updated to asserts and now the test fails, no exceptions are
    # being raised and it seems to be in 3rd party code

    idf = ef.get_idf()

    # eppy key-inputs should reject bad key values at setup
    r: Parameter = Parameter(FieldSelector(class_name="invalid", field_name="any"))

    with pytest.raises(Exception):
        r.setup(idf)
    print("Invalid object key detected successfully.")
    r = Parameter(
        FieldSelector(object_name="NonRes Fixed Assembly Window", field_name="invalid")
    )
    with pytest.raises(Exception):
        r.setup(idf)
    print("Invalid property detected successfully.")


def test_setup_changes():
    idf = ef.get_idf()

    r1 = Parameter(
        FieldSelector(object_name="NonRes Fixed Assembly Window", field_name="UFactor"),
        value_descriptors=RangeParameter(min_val=0.1, max_val=5),
    )
    r2 = wwr()
    r3 = wwr(value_descriptor=RangeParameter(0.01, 0.99, name="other"))

    r1.setup(idf)
    r2.setup(idf)
    assert len(idf.idfobjects["FENESTRATIONSURFACE:DETAILED"]) == 4, "bug in r2.setup"

    idf = ef.get_idf()
    assert len(idf.idfobjects["FENESTRATIONSURFACE:DETAILED"]) == 21, "bad idf"
    r3.setup(idf)
    assert len(idf.idfobjects["FENESTRATIONSURFACE:DETAILED"]) == 4, "bug in r3.setup"

    print("setup tests done")


def test_custom_evaluation(regtest):
    """check to see if descriptors display as intended, and check to make sure custom
    evaluations work with EvaluatorGeneric"""

    # create the descriptors
    zero_to_nine = RangeParameter(min_val=0, max_val=9, name="0-9")
    single_digit_integers = CategoryParameter(
        options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], name="single digit"
    )
    text_example = CategoryParameter(options=["a", "b", "c", "other"], name="text")

    # create the parameters and the problem
    parameters = [
        Parameter(value_descriptors=zero_to_nine),
        Parameter(value_descriptors=single_digit_integers),
        Parameter(value_descriptors=text_example),
    ]
    problem = Problem(parameters, outputs=["output"])

    # create the sampling distribution (seeded with only one output to give consistent
    # outputs after evaluating)
    samples = sampling.dist_sampler(sampling.seeded_sampler, problem, num_samples=1)
    with regtest:
        print(samples)

    # custom evaluation function from the jupyter notebook
    def evaluation_function(values):
        x, y, z = values
        if z == "other":
            return (0,)
        else:
            return (x * y,)

    evaluator = EvaluatorGeneric(evaluation_function, problem)
    # The evaluator will use this objective by default
    outputs = evaluator.df_apply(samples, keep_input=True)
    result = outputs.iloc[0]["output"]
    with regtest:
        print(f"{result:.5E}")


@pytest.fixture
def range_zero_to_one():
    return RangeParameter(0, 1, name="zero to one")


@pytest.fixture
def range_zero_to_five():
    return RangeParameter(0, 5, name="zero to five")


@pytest.fixture
def range_unnamed():
    return RangeParameter(0, 5)


@pytest.fixture
def category_abc():
    return CategoryParameter(["A", "B", "C"], name="ABC")


@pytest.fixture
def multiple_descriptor_parameter(range_zero_to_one, category_abc):
    return Parameter(
        value_descriptors=[range_zero_to_one, category_abc, range_zero_to_one]
    )


def test_multiple_descriptor_names(multiple_descriptor_parameter):
    assert Problem([multiple_descriptor_parameter]).names() == ["zero to one", "ABC"]


def test_multiple_descriptor_sampling(multiple_descriptor_parameter):
    problem = Problem([multiple_descriptor_parameter])
    samples = sampling.dist_sampler(sampling.lhs, problem, 5)
    assert len(samples.columns) == 2


def test_problem_value_descriptors(range_zero_to_five, range_zero_to_one, category_abc):
    problem = Problem(
        [
            Parameter(value_descriptors=lst)
            for lst in [
                [range_zero_to_one, range_zero_to_five],
                [category_abc, range_zero_to_one],
                [category_abc],
            ]
        ]
    )
    assert problem.num_inputs == 3
    assert problem.value_descriptors == [
        range_zero_to_one,
        range_zero_to_five,
        category_abc,
    ]


@pytest.mark.compatibility
def test_parameter_name_transfers_to_descriptor(range_unnamed):
    with pytest.warns(
        DeprecationWarning,
        match=r"Call to deprecated function \(or staticmethod\) value_descriptor.",
    ):
        Parameter(value_descriptors=range_unnamed, name="foo")
    assert range_unnamed.name == "foo"


@pytest.mark.compatibility
def test_parameter_name_does_not_overwrite(range_zero_to_five):
    old_name = range_zero_to_five.name
    with pytest.warns(None) as record:
        Parameter(value_descriptors=range_zero_to_five, name="foo")
    assert (
        "This parameter's descriptor is already named"
        in record.pop(UserWarning).message.args[0]
    )
    assert (
        "Call to deprecated function (or staticmethod) value_descriptor."
        in record.pop(DeprecationWarning).message.args[0]
    )
    assert range_zero_to_five.name == old_name


def test_abstractfield_arithmetic(building):
    mode = ef.get_mode(building)
    if mode == "idf":
        index = None
        for obj in building.idfobjects[
            "MATERIAL"
        ]:  # for loop to find index of "Mass NonRes Wall Insulation"
            if obj.Name == "Mass NonRes Wall Insulation":
                index = building.idfobjects["MATERIAL"].index(obj)
                break
        start = float(
            building.idfobjects["MATERIAL"][index].Thickness
        )  # chose arbitrarly as it has thickness values to work with
        testSelector = FieldSelector(
            class_name="MATERIAL",
            object_name="Mass NonRes Wall Insulation",
            field_name="Thickness",
        )
        testSelector.multiply(building, 2)
        testSelector.add(building, -0.03)  # arbitrary numbers to check for arithmetic
        end = building.idfobjects["MATERIAL"][index].Thickness
    else:
        start = building["Material"]["Mass NonRes Wall Insulation"][
            "thickness"
        ]  # chose arbitrarly as it has thickness values to work with
        testSelector = FieldSelector(
            class_name="Material",
            object_name="Mass NonRes Wall Insulation",
            field_name="thickness",
        )
        testSelector.multiply(building, 2)
        testSelector.add(building, -0.03)
        end = building["Material"]["Mass NonRes Wall Insulation"]["thickness"]
    assert (start * 2) - 0.03 == end
