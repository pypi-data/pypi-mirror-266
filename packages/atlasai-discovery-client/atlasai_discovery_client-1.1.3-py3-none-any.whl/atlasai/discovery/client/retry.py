from contextlib import contextmanager
from functools import wraps
import logging
import os
import time

from . import constants
from .environ import environment

MAX_ATTEMPTS_KEY = 'DISCOVERY_CLIENT_MAX_RETRY_ATTEMPTS'
MAX_ATTEMPTS = 5
if MAX_ATTEMPTS_KEY in os.environ:
    MAX_ATTEMPTS = os.environ[MAX_ATTEMPTS_KEY]

__all__ = [
    'retry',
    'enable_retry',
]

logger = logging.getLogger(__name__)

class RetryOperation:
    def __init__(self, *error_types, attempts=None, backoff_factor=0.2):
        self.error_types = tuple(error_types or [Exception])
        self.attempts = attempts
        self.backoff_factor = backoff_factor

    @property
    def attempts(self):
        return self._attempts

    @attempts.setter
    def attempts(self, value):
        if value is None:
            value = MAX_ATTEMPTS

        assert isinstance(value, int), '`attempts` must be an integer'
        self._attempts = value

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            num_attempts = 1
            if os.getenv(constants.ENABLE_DISCOVERY_RETRIES):
                num_attempts = self.attempts

            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except self.error_types:
                    attempt += 1
                    if attempt >= num_attempts:
                        raise

                    sleep_for = self.backoff_factor * pow(2, attempt)
                    logger.info(f'Failed attempt #{attempt}. Retrying after sleeping for {sleep_for} seconds')
                    time.sleep(sleep_for)

        return wrapper

retry = RetryOperation

@contextmanager
def enable_retry():
    with environment(**({
        constants.ENABLE_DISCOVERY_RETRIES: '1'
    })):
        yield
