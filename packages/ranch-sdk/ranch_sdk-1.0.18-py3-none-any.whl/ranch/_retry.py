import time
import requests
from .exceptions import InvalidKeyException, EmptySafeException


# TRANSIENT_ERROR_CODES = [
#     429,
#     500,
#     502,
#     503,
#     504,
# ]


def retry(request_func, max_retries=3):
    def wrapper(*args, **kwargs):
        attempts = 0
        response = None
        while attempts < max_retries:
            try:
                response = request_func(*args, **kwargs)

            except requests.exceptions.RequestException as e:
                time.sleep(2)
                attempts += 1
                # continue

            if response.ok:
                return response

            # if response.status_code == 401:
            #     return response.status_code

            #     raise InvalidKeyException("incorrect API Key")
            # elif response.status_code == 402:
            #     raise EmptySafeException("Your safe is too low")
            # else:
            #     return response
            #     response.raise_for_status()
            #     raise Exception(f"Unknown error ({response.status_code})")

    return wrapper
