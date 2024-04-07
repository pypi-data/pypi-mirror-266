"""
Template and interface classes that handle evaluator inputs and outputs.
"""

# Python Core Libraries
from abc import ABC, abstractmethod
from typing import Union


class ReprMixin(ABC):
    """Adds a useful string representation to subclasses"""

    def __init__(self):
        self._to_repr = {}

    def _add_repr(self, name, attr=None, check=False):
        if attr is None:
            attr = name
        if (not check) or getattr(self, attr):
            self._to_repr[name] = attr

    def _add_reprs(self, names, check=False):
        for name in names:
            self._add_repr(name, check=check)

    def __repr__(self):
        attr_list = [
            f"{attr_name}={repr(getattr(self, attr))}"
            for attr_name, attr in self._to_repr.items()
        ]
        return f'{self.__class__.__name__}({", ".join(attr_list)})'


class IOBase(ReprMixin, ABC):
    """Base class for inputs, objectives and constraints.

    `name` is used for generating DataFrame column titles."""

    def __init__(self, name=""):
        super().__init__()
        self._name = name
        self._add_repr("name", "_name", True)

    @property
    def name(self):
        return self._name or self._default_name

    @name.setter
    def name(self, value):
        self._name = value

    _default_name = ""

    def has_default_name(self):
        """

        :return: True if this object is using its default name, false otherwise
        """
        return not self._name


def get_name(x: Union[str, int, IOBase]):
    if isinstance(x, str):
        return x
    if isinstance(x, int):
        return str(x)
    return x.name


class Descriptor(IOBase, ABC):
    """Base class for descriptors.

    Descriptors describe a set of possible values for a single input.
    They are used in :class:`Parameters <parameters.Parameter>` to specify
    the possible input space.
    """

    def __init__(self, name=""):
        super().__init__(name=name)
        self.platypus_type = NotImplemented

    @abstractmethod
    def validate(self, value) -> bool:
        """Checks if `value` is a valid value for this Descriptor.

        :param value: The value to check.
        :return: True if the value is valid False otherwise
        """

    # consider a pandas type to improve DataFrame generation
    @abstractmethod
    def sample(self, value):
        """Takes a value in the range 0-1 and returns a valid value for this parameter"""
        pass

    _default_name = "input"


class AnyValue(Descriptor):
    """A :class:`Descriptor` that can take on any possible value.
    Intended to be used as a placeholder."""

    def validate(self, value) -> bool:
        """All values are accepted by this :class:`Descriptor`,
        so validate always returns True

        :param value: The value to validate
        :return: True
        """
        return True

    def sample(self, value):
        """This is a placeholder descriptor. Therefore, sampling is not possible."""
        raise NotImplementedError

    def __bool__(self):
        """Marks this as a 'missing' piece"""
        # ReprMixin will detect this as something to not include when checking
        return False


class Selector(ReprMixin, ABC):
    """Base Class for Selectors, which describe what attribute of the model is read or modified"""

    @abstractmethod
    def get(self, building):
        """Get the current value of this attribute of the building

        :param building:
        :return:
        """
        pass

    @abstractmethod
    def set(self, building, value):
        """Modifies `building`, setting the attribute this selector corresponds to to `value`

        :param building: the building to modify.
        :param value: the value to set this selector's attribute to.
        :return:
        """
        pass

    def setup(self, building) -> None:
        """Modifies the building so that it is ready for this selector"""
        pass


class DummySelector(Selector):
    """A selector that does not modify the building.
    Intended to be used as a placeholder."""

    def get(self, building):
        """Getting the value of this placeholder is not possible.

        This function will raise a NotImplementedError.
        """
        raise NotImplementedError

    def set(self, building, value):
        """This placeholder will not do anything with the given value."""
        pass

    def __bool__(self):
        """Marks this as a 'missing' piece"""
        # ReprMixin will detect this as something to not include when checking
        return False


class Objective(IOBase):
    """Base class for objectives."""

    def __call__(self, *args, **kwargs) -> float:
        """Return the objective's value on the instance represented by *args and **kwargs"""
        raise NotImplementedError
