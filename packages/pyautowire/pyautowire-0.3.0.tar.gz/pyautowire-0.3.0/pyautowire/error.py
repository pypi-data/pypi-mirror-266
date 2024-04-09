class ParameterNotInSignatureError(Exception):
    """
    Exception raised when autowiring is requested for a parameter that does not exist in the function signature.
    """

    def __init__(self, parameter: str):
        self.parameter = parameter
        self.message = f"Parameter '{self.parameter}' specified in @pyautowire decorator is not in the function signature"
        super().__init__(self.message)


class ParameterNotInCacheError(Exception):
    """
    Exception raised when autowiring is requested for a parameter that does not exist in kink's `di` container.
    """

    def __init__(self, parameter: str):
        self.parameter = parameter
        self.message = f"Parameter '{self.parameter}' does not exist in the 'di' cache"
        super().__init__(self.message)


class ParameterNotInjectableError(Exception):
    """
    Exception raised when autowiring is requested for aparameter that is not an Injectable.
    """

    def __init__(self, parameter: str):
        self.parameter = parameter
        self.message = f"Parameter '{self.parameter}' is not an Injectable"
        super().__init__(self.message)
