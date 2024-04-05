import inspect
from pyautowire import cache

from pyautowire.error import ParameterNotInSignatureError, ParameterNotInCacheError

from pyautowire.injectable import Injectable


def autowire(*autowire_params):
    """
    Decorator that autowires the specified parameters of a function.
    Parameters are autowired if they
    - Are specified in the decorator arguments
    - Are of a class that is a subclass of Injectable
    - They exist within kink's dependency injection container
    :param autowire_params: names of parameters to pyautowire
    :return: fully autowired function
    """

    def decorator(func):
        sig = inspect.signature(func)

        def wrapper(*args, **kwargs):
            for (
                name
            ) in autowire_params:  # Check if the parameter is in the pyautowire list
                if name not in sig.parameters:
                    raise ParameterNotInSignatureError(name)
                param = sig.parameters[name]
                param_type = param.annotation
                if inspect.isclass(param_type) and issubclass(param_type, Injectable):
                    if not cache.contains(param_type):
                        raise ParameterNotInCacheError(
                            param_type.get_fully_qualified_name()
                        )
                    kwargs[name] = cache.get(param_type)
            return func(*args, **kwargs)

        return wrapper

    return decorator
