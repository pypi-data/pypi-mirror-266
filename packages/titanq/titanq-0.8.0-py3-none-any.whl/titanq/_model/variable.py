import abc
import enum
from typing import List, Tuple
import numpy as np
from numpy._typing import NDArray

class Vtype(str, enum.Enum):
    BINARY = 'binary'
    BIPOLAR = 'bipolar'
    INTEGER = 'integer'

    def __str__(self) -> str:
        return str(self.value)

class VariableVector(abc.ABC):
    """
    Object That represent a vector of variable to be optimized.
    """
    def __init__(self, name: str, size: int) -> None:
        if size < 1:
            raise ValueError("Variable vector size cannot be less than 1")

        self._name = name
        self._size = size


    def size(self) -> int:
        """
        :return: size of this vector.
        """
        return self._size


    def name(self) -> str:
        """
        :return: Name of this variable vector.
        """
        return self._name


    @abc.abstractmethod
    def vtype(self) -> Vtype:
        """
        :return: Type of variable in the vector.
        """


    @abc.abstractmethod
    def variable_types_as_list(self) -> str:
        """
        :return: Generate a string of 'b' or 'i' depending on the variable type
        """


    @abc.abstractmethod
    def variable_bounds(self) -> NDArray:
        """
        :return: The variable bounds associated to this variable vector
        """


class BinaryVariableVector(VariableVector):
    def vtype(self) -> Vtype:
        return Vtype.BINARY


    def variable_types_as_list(self) -> str:
        return "b" * self.size()


    def variable_bounds(self) -> NDArray:
        return np.tile(np.array([0,1], dtype=np.float32), (self._size, 1))


# This class violate the Liskov Substitution Principle because it raise error in some of
# the method it need to implement. This is somewhat fine for now but should be fix soon.
class BipolarVariableVector(VariableVector):
    def vtype(self) -> Vtype:
        return Vtype.BIPOLAR

    def variable_types_as_list(self) -> str:
        raise ValueError("Cannot set variable types as a list for 'bipolar' variable type")

    def variable_bounds(self) -> NDArray:
        raise ValueError("Cannot define variable bounds for 'bipolar' variable type")


class IntegerVariableVector(VariableVector):
    def __init__(self, name: str, size: int, variable_bounds: List[Tuple[int, int]]) -> None:
        super().__init__(name, size)

        if len(variable_bounds) != self.size():
            raise ValueError("variable_bounds need to be the same length as variable size")

        self._variable_bounds = np.array(variable_bounds, dtype=np.float32)


    def vtype(self) -> Vtype:
        return Vtype.INTEGER


    def variable_types_as_list(self) -> str:
        return "i" * self.size()


    def variable_bounds(self) -> NDArray:
        return self._variable_bounds