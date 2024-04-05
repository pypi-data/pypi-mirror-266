class ParameterNotInSignatureError(Exception):
    def __init__(self, parameter: str):
        self.parameter = parameter
        self.message = f"Parameter '{self.parameter}' specified in @pyautowire decorator is not in the function signature"
        super().__init__(self.message)


class ParameterNotInCacheError(Exception):
    def __init__(self, parameter: str):
        self.parameter = parameter
        self.message = f"Parameter '{self.parameter}' does not exist in the 'di' cache"
        super().__init__(self.message)
