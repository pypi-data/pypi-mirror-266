"""
Module with all the decorators commonly used
"""

import os
import sys
import traceback
from typing import Callable, Union


def try_catch_log(function: Callable) -> Callable:
    """
        Decorator to catch and log exceptions.

    Args:
        function (function): The function to decorate.

    Returns:
        function: The decorated function.
    """

    def wrapper_fun(*args, **kwargs) -> Union[Callable, None]:
        try:
            return function(*args, **kwargs)
        except Exception:
            print(traceback.format_exc())
            # Print also args and kwargs
            print(f"[ERROR] args: {args}")
            print(f"[ERROR] kwargs: {kwargs}")
            return None

    return wrapper_fun


def try_catch(function: Callable) -> None:
    """
    Decorator to run a function within a try-catch block and
    print the result in case of an error.

    Args:
        function (Callable): Function to run
    """

    def wrapper_fun(*args, **kwargs) -> Union[Callable, None]:
        try:
            return function(*args, **kwargs)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            # Get next traceback because this one belongs to this wrapper
            exc_tb = exc_tb.tb_next

            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            file = os.path.splitext(fname)[0]

            error_summary = (
                f"Exception error on file '{file}.py' function '{function.__name__}':"
                f" {e}, {exc_type}, {fname}, {exc_tb.tb_lineno}"
            )
            print(error_summary)
            traceback.print_exc()
            full_traceback = traceback.format_exception(type(e), e, e.__traceback__)
            full_traceback = "".join(full_traceback)
