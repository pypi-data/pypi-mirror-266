import logging
from os import environ

__all__ = [
    'environment',
]

logger = logging.getLogger(__name__)

class EnvironContext:
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def __enter__(self):
        self._environ = {
            k: environ.get(k)
            for k in self._kwargs.keys()
        }

        for k, v in self._kwargs.items():
            if v is not None:
                environ[k] = v
                logger.debug(f'Set env var: {k} => {v}')
            elif environ.get(k) is not None:
                del environ[k]
                logger.debug(f'Cleared env var: {k} => {v}')

    def __exit__(self, *args, **kwargs):
        for k, v in self._environ.items():
            if v is not None:
                environ[k] = v
                logger.debug(f'Restored env var: {k} => {v}')
            elif environ.get(k) is not None:
                del environ[k]
                logger.debug(f'Cleared env var: {k} => {v}')

environment = EnvironContext
