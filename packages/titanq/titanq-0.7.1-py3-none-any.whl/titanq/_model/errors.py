class TitanQError(Exception):
    """Base TitanQ error"""

class MaximumVariableLimitError(TitanQError):
    """Variable already defined in the model"""

class MissingVariableError(TitanQError):
    """Variable has not already been registered"""

class MissingObjectiveError(TitanQError):
    """Objective has not already been registered"""

class MaximumConstraintLimitError(TitanQError):
    """The number of constraints is bigger than the number of variables"""

class ConstraintSizeError(TitanQError):
    """The constraint size does not match"""

class ObjectiveAlreadySetError(TitanQError):
    """An objective has already been set"""

class OptimizeError(TitanQError):
    """Error occur during optimization"""

class ServerError(TitanQError):
    """Error returned by the server"""

class ConnectionError(TitanQError):
    """Error due to a connection issue with an external resource"""