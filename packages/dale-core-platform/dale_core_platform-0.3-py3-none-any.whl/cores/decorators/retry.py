from functools import wraps
import time
from typing import Callable, Any

from cores.const.custom_exception import RequestTimeout
from cores.utils.common.logger_util import logger


def retry(max_retries: int = 2, retry_exceptions: tuple = (TimeoutError, ConnectionError, RequestTimeout)) -> Callable:
    """_summary_

    Args:
        max_retries (int, optional): _description_. Defaults to 2.
        retry_exceptions (tuple, optional): _description_. Defaults to (TimeoutError, ConnectionError).

    Usage:
        @retry(max_retries=3)
        def my_function():
            # Your function's logic here
            print("Function called")
            raise TimeoutError("Timeout occurred")

    Returns:
        Callable: _description_
    """
    def decorator_retry(func: Callable) -> Callable:
        @wraps(func)
        def wrapper_retry(*args, **kwargs) -> Any:
            for retry_count in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    return result
                except retry_exceptions as e:
                    if retry_count < max_retries:
                        logger.info(
                            f"Function failed, doing retry {retry_count + 1}/{max_retries} - {e}")
                        time.sleep(1)  # Wait for a moment before retrying
                    else:
                        raise RequestTimeout(
                            f"Failed after {max_retries} retries. Aborted!")
        return wrapper_retry
    return decorator_retry
