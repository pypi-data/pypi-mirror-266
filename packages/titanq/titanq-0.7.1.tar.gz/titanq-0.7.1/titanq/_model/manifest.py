
class Manifest:
    """
    This class tracks gives us more insignt on the different numpy data used.
    """
    def __init__(self) -> None:
        self._has_cardinality_constraint: bool = False
        self._has_set_partitioning_constraint: bool = False
        self._has_equality_constraint: bool = False
        self._has_inequality_constraint: bool = False

    def activate_set_partitioning_constraint(self) -> None:
        """
        Declares set partitioning constraint is being used.
        """
        self._has_set_partitioning_constraint = True

    def activate_cardinality_constraint(self) -> None:
        """
        Declares cardinality constraint is being used.
        """
        self._has_cardinality_constraint = True

    def activate_equality_constraint(self) -> None:
        """
        Declares equality constraint is being used.
        """
        self._has_equality_constraint = True

    def activate_inequality_constraint(self) -> None:
        """
        Declares inequality constraint is being used.
        """
        self._has_inequality_constraint = True

    def has_set_partitioning_constraint(self) -> bool:
        """
        :return: if the manifest has set partitioning constraint.
        """
        return self._has_set_partitioning_constraint

    def has_cardinality_constraint(self) -> bool:
        """
        :return: if the manifest has cardinality constraint.
        """
        return self._has_cardinality_constraint

    def has_equality_constraint(self) -> bool:
        """
        :return: if the manifest has equality constraint.
        """
        return self._has_equality_constraint

    def has_inequality_constraint(self) -> bool:
        """
        :return: if the manifest has inequality constraint.
        """
        return self._has_inequality_constraint