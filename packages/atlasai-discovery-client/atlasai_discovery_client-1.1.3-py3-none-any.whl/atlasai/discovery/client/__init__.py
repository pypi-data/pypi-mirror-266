# flake8: noqa
import os
import os.path as osp

from dotenv import load_dotenv

# do this first!
from .init import configure_logging
configure_logging()
del configure_logging

from . import (
    instance,
    instances,
    product,
    products,
    release,
    releases,
    reference,
)
from .other import (
    authenticate,
    distinct,
    entities,
    search,
    get_download_uris,
)
from .utils import (
    paginator,
    paginate
)

env_file = osp.join(osp.dirname(__file__), '.env')
if osp.exists(env_file):
    load_dotenv(env_file)

if not os.getenv('DISCOVERY_GRAPHQL_URL'):
    raise RuntimeError(f'Missing required environment variable: DISCOVERY_GRAPHQL_URL')

del load_dotenv
del env_file
del osp
del os
