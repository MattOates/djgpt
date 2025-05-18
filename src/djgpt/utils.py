import time
from functools import wraps
from os import getenv
from typing import Callable, Optional, Type

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

from rich.console import Console  # noqa: E402
from rich.prompt import Confirm  # noqa: E402

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
    prompt: Optional[str] = None,
    cooloff: bool = False,
) -> Callable:
    """Retry calling a wrapped function.

    Helper decorator to deal with the various troubles with integrating against so many external pieces of tech.
    GPT especially might just halucinate invalid JSON, though the prompt so far does a good job.

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
    cooloff : bool
        Use linear backoff per tries (try * sleeptime)
    """

    def decorator_retry(func):
        @wraps(func)
        def wrapper_retry(*args, **kwargs):
            attempt = 1
            while attempt <= num_attempts:
                debug(f"Attempt {attempt} for {func.__name__}")
                try:
                    result = func(*args, **kwargs)
                    if none_is_fail and result is None:
                        raise ValueError("Function returned None.")
                    return result
                except exception_class as e:
                    debug(f"Exception occurred: {e}, retrying...")
                    if prompt:
                        if not Confirm.ask(prompt, default=False):
                            debug("User answered no, breaking out of retry")
                            break
                    attempt += 1
                    if attempt <= num_attempts:
                        wait_time = sleeptime
                        if cooloff:
                            wait_time = sleeptime * attempt
                        if wait_time > 0:
                            time.sleep(wait_time)
            return None

        return wrapper_retry

    if _func is None:
        return decorator_retry
    else:
        return decorator_retry(_func)
