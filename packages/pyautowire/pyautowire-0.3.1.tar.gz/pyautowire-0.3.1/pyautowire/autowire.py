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
                # If the parameter has been provided in kwargs, skip
                if arg_name in kwargs:
                    continue
                param = sig.parameters[arg_name]
                param_type = param.annotation
                # Check if parameter is of type injectable. This could actually be skipped in the future.
                # Technically, the only way to write something to the cache with the given abstraction is to use
                # Injectable.register(), but maybe this mechanism could be changed in the future.
                if not is_injectable(param_type):
                    raise ParameterNotInjectableError(param_type)
                # Check if the parameter is in the cache
                if cache.contains(param_type):
                    logging.debug(
                        "Cache hit for class %s", param_type.get_fully_qualified_name()
                    )
                    kwargs[arg_name] = cache.get(param_type)
                else:
                    # Check if an alias for the parameter exists in the cache
                    if cache.contains_alias(arg_name):
                        logging.debug("Cache hit for alias %s", arg_name)
                        kwargs[arg_name] = cache.get_alias(arg_name)
                        continue
                    else:
                        # Nothing found, raise Error.
                        raise ParameterNotInCacheError(
                            param_type.get_fully_qualified_name()
                        )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def is_injectable(param_type):
    return inspect.isclass(param_type) and issubclass(param_type, Injectable)
