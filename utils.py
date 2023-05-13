import time
from functools import wraps
from os import getenv
from typing import Optional, Callable, Type

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv(usecwd=True))

from rich.console import Console
from rich.prompt import Confirm

CONSOLE = Console()
LOGLEVEL = getenv("LOGLEVEL", "INFO")


def debug(whatever: object):
    """Hacky debug level print."""
    if LOGLEVEL == "DEBUG" or LOGLEVEL == "TRACE":
        CONSOLE.log(whatever)


def retry(
    _func: Optional[Callable] = None,
    num_attempts: int = 3,
    exception_class: Type[BaseException] = Exception,
    sleeptime: int = 0,
    none_is_fail: bool = True,
    prompt: Optional[str] = None
) -> Callable:
    """Retry calling a wrapped function.

    Helper decorator to deal with the various troubles with integrating against so many external pieces of tech.
    GPT especially might just halucinate invalid JSON, though the prompt so far does a good job.
    ...

    Parameters
    ----------
    _func : Callable, optional
        Used to deal with recognising if we are dealing with @retry or @retry(some=param)
    num_attempts : int
        Defaults to 3, try as many times as you want
    exception_class : Type[BaseException]
        Defaults to catching all exceptions and retrying
    sleeptime : int
        Time to wait before trying again default 0s
    none_is_fail : bool
        Defaults to True so we deal with None result as a failure to retry
    prompt : str, optional
        A y/n question to ask the user waiting on their input before retrying incase they have to do something

    Returns
    -------
    object
        a callable wrapped function, or what it returned depending on if parameters were passed to the decorator
    """
    def decorator_retry(func: Callable):
        @wraps(func)
        def wrapper_retry(*args, **kwargs):
            for i in range(num_attempts):
                try:
                    returned = func(*args, **kwargs)
                    if none_is_fail and returned is None:
                        CONSOLE.log(f"[bold yellow]Failed with None returned, trying again...")
                        time.sleep(sleeptime)
                        if prompt is not None:
                            Confirm.ask(prompt)
                        continue
                    return returned
                except exception_class as e:
                    if i == num_attempts - 1:
                        raise
                    else:
                        CONSOLE.log(f"[bold yellow]Failed with error {e}, trying again...")
                        time.sleep(sleeptime)
                        if prompt is not None:
                            Confirm.ask(prompt)
            return None
        return wrapper_retry

    if _func is None:
        return decorator_retry
    else:
        return decorator_retry(_func)
