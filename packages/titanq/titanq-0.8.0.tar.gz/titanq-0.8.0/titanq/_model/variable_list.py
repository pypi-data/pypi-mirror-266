from typing import Dict, List, Set, Tuple

from .variable import VariableVector, Vtype
from .errors import VariableAlreadyExist

import numpy as np
from numpy._typing import NDArray

class VariableVectorList:
    def __init__(self) -> None:
        self._variables: List[VariableVector] = []
        self._variables_name: Set[str] = set()


    def add(self, v: VariableVector):
        """
        Add a variable vector to this list

        :param v: the new variable vector to add

        :raise VariableAlreadyExist: If a the variable to be add has the same name as an existing variable in this list
        """
        name = v.name()
        if name in self._variables_name:
            raise VariableAlreadyExist(f"variable with name: {name} has already been defined")

        self._variables_name.add(name)
        self._variables.append(v)


    def total_variable_size(self) -> int:
        """ :return: total size of all variables vector contained in the list """
        return sum(v.size() for v in self._variables)


    def n_variables(self) -> int:
        """ :return: The number of variable vector in the list """
        return len(self._variables)


    def get_variable_types_str(self, equality_constraint: bool, inequality_constraint: bool) -> str:
        """
        Generate the variable types string for all the variable of this list.

        :param equality_constraint: indicate if the problem has equality constraint
        :param inequality_constraint: indicate if the problem has inequality constraint

        :return: The generated variable type string for all the variables
        """
        n_variable = self.n_variables()

        if n_variable == 0:
            return ""

        elif n_variable == 1:
            variable = self._variables[0]
            if equality_constraint or inequality_constraint:
                return variable.variable_types_as_list()
            elif variable.vtype() is Vtype.INTEGER:
                return variable.variable_types_as_list()
            else:
                return str(variable.vtype())

        else: # n_variable > 1
            return "".join(v.variable_types_as_list() for v in self._variables)


    def has_variable_of_type(self, vtype: Vtype) -> bool:
        """:return: If any of the variable in this list has the given type"""
        return any(v.vtype() is vtype for v in self._variables)


    def variable_bounds(self) -> NDArray:
        """return the variable bounds of all variable in this list"""
        return np.concatenate([v.variable_bounds() for v in self._variables])


    def __iter__(self):
        return iter(self._variables)