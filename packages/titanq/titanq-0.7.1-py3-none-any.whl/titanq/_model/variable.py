import enum
import numpy as np

class Vtype(str, enum.Enum):
    BINARY = 'binary'
    BIPOLAR = 'bipolar'

    def __str__(self) -> str:
        return str(self.value)

class VariableVector:
    """
    Object That represent a vector of variable to be optimized.
    """
    def __init__(self, name='', size=1, vtype=Vtype.BINARY) -> None:
        if size < 1:
            raise ValueError("Variable vector size cannot be less than 1")

        self._name = name
        self._size = size
        self._vtype = vtype


    def size(self) -> int:
        """
        :return: size of this vector.
        """
        return self._size

    def vtype(self) -> Vtype:
        """
        :return: Type of variable in the vector.
        """
        return self._vtype

    def name(self) -> str:
        """
        :return: Name of this variable vector.
        """
        return self._name

    def variable_types_as_list(self) -> str:
        """
        :return: Generate a string of 'b' depending on the variable size
        """
        if self._vtype == Vtype.BIPOLAR:
            raise ValueError("Cannot set variable types as a list for 'bipolar' type")

        return "".join(['b' for _ in range(self._size)])

    def create_variable_bounds(self):
        """
        :return: Generate a string of 'b' depending on the variable size
        """
        if self._vtype == Vtype.BIPOLAR:
            raise ValueError("Cannot set variable types as a list for 'bipolar' type")

        return np.tile(np.array([0,1]), (self._size, 1))