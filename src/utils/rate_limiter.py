from ratelimit import limits, sleep_and_retry
from functools import wraps
import time

# Rate limits for different APIs
ONE_MINUTE = 60
ETHERSCAN_CALLS = 5  # 5 calls per minute
GEMINI_CALLS = 60    # 60 calls per minute

@sleep_and_retry
@limits(calls=ETHERSCAN_CALLS, period=ONE_MINUTE)
def etherscan_rate_limit():
    """Rate limiter for Etherscan API"""
    return

@sleep_and_retry
@limits(calls=GEMINI_CALLS, period=ONE_MINUTE)
def gemini_rate_limit():
    """Rate limiter for Gemini API"""
    return

def with_retry(max_retries=3, delay=1):
    """Decorator for retrying failed API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise e
                    time.sleep(delay * retries)
            return None
        return wrapper
    return decorator 