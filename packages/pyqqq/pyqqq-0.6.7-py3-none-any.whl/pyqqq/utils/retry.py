import time
from functools import wraps

def retry(exceptions, total_tries=5, delay=0.5, backoff=2, silently: bool = False):
    """
    Decorator for retrying function if exception occurs

    Args:
        exceptions (Exception or tuple): exception(s) to check. can be a tuple of exceptions
        total_tries (int): total tries to attempt
        delay (float): initial delay between retry in seconds
        backoff (float): backoff multiplier e.g. value of 2 will double the delay each retry
        silently (bool): if True, will not print exception message
    Returns:
        function: Decorated function that will retry upon exceptions
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_try = 0
            while current_try < total_tries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    current_try += 1
                    sleep_time = delay * (backoff ** (current_try - 1))
                    if current_try != total_tries:
                        if not silently:
                            print(f"{str(e)}\nRetrying in {sleep_time} seconds...")
                        time.sleep(sleep_time)
                    else:
                        print("Max retry attempts reached, aborting.")
                        raise
        return wrapper
    return decorator