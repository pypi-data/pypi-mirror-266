class TitanQError(Exception):
    """Base TitanQ error"""

class MissingVariableError(TitanQError):
    """Variable has not already been registered"""

class VariableAlreadyExist(TitanQError):
    """Variable with the same name already exist"""

class MissingObjectiveError(TitanQError):
    """Objective has not already been registered"""

class MaximumConstraintLimitError(TitanQError):
    """The number of constraints is bigger than the number of variables"""

class ConstraintSizeError(TitanQError):
    """The constraint size does not match"""

class ConstraintAlreadySetError(TitanQError):
    """A constraint has already been set"""

class ObjectiveAlreadySetError(TitanQError):
    """An objective has already been set"""

class OptimizeError(TitanQError):
    """Error occur during optimization"""

class ServerError(TitanQError):
    """Error returned by the server"""

class ConnectionError(TitanQError):
    """Error due to a connection issue with an external resource"""