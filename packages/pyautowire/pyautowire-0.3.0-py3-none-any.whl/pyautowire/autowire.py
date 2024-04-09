import inspect
import logging

from pyautowire import cache

from pyautowire.error import (
    ParameterNotInSignatureError,
    ParameterNotInCacheError,
    ParameterNotInjectableError,
)

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
                arg_name
            ) in autowire_params:  # Check if the parameter is in the pyautowire list
                if arg_name not in sig.parameters:
                    raise ParameterNotInSignatureError(arg_name)
                param = sig.parameters[arg_name]
                param_type = param.annotation
                if not is_injectable(param_type):
                    raise ParameterNotInjectableError(param_type)
                if cache.contains(param_type):
                    logging.debug(
                        "Cache hit for class %s", param_type.get_fully_qualified_name()
                    )
                    kwargs[arg_name] = cache.get(param_type)
                else:
                    if cache.contains_alias(arg_name):
                        logging.debug("Cache hit for alias %s", arg_name)
                        kwargs[arg_name] = cache.get_alias(arg_name)
                        continue
                    else:
                        raise ParameterNotInCacheError(
                            param_type.get_fully_qualified_name()
                        )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def is_injectable(param_type):
    return inspect.isclass(param_type) and issubclass(param_type, Injectable)
