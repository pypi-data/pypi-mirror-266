import time
from contextlib import contextmanager
from functools import wraps
from typing import Callable, TypeVar
from dalpha.logging import logger
T = TypeVar("T")

def log_function(
    start_logging_message: str = "started",
    end_logging_message: str = "completed",
    logs_result: bool = False,
    function_name: str = None,
) -> Callable[..., T]:
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = function_name if function_name else func.__name__
            log_data = {
                "function_name": func_name
            }
            logger.info(
                message = f"{func_name}: {start_logging_message}",
                data = log_data,
            )
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            if logs_result:
                log_data["result"] = result
            log_data["duration"] = end_time - start_time
            logger.info(
                message = f"{func_name}: {end_logging_message}",
                data = log_data,
            )
            return result

        return wrapper

    return actual_decorator

# contextmanager that logs function
@contextmanager
def log_block(
    start_logging_message: str = "started",
    end_logging_message: str = "completed",
    block_name: str = None,
):
    metadata = {
        "block_name": block_name,
    }
    logger.info(
        message = f"{block_name}: {start_logging_message}",
        data = metadata,
    )
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        metadata["duration"] = end_time - start_time
        logger.info(
            f"{block_name}: {end_logging_message}",
            data = metadata,
        )
