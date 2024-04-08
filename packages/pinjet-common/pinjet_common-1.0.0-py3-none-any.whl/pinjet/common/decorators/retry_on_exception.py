import functools
from typing import Callable, Any, Type


def retry_on_exception(func: Callable = None,
                       retries: int = 1,
                       exception_type: Type[Exception] = None) -> Any:

    def decorator_retry(function: Callable) -> Callable:

        @functools.wraps(function)
        def wrapper(*args, **kwargs):

            caught_exception = None

            for _ in range(retries):

                try:

                    return function(*args, **kwargs)

                except Exception as caught_exception:

                    if not __should_retry(exception_type, caught_exception, retries):

                        raise caught_exception

            raise caught_exception  # Retry exhausted, raise the last exception

        return wrapper

    # Check if no arguments are provided to the decorator
    if func is None:

        return decorator_retry

    else:

        return decorator_retry(func)


def __should_retry(exception_type, exception, retries):
    """
    Check if the exception should trigger a retry.
    """

    if exception_type is None or isinstance(exception, exception_type):

        return retries > 1

    return False