import hmac
try:
    from importlib.metadata import version # python >= 3.8
except ImportError:
    from pkg_resources import get_distribution # python < 3.8
import logging
import os
import threading
from urllib.parse import urlparse
import warnings

import arrow
import requests
from requests.adapters import HTTPAdapter, Retry
from sgqlc.endpoint.requests import RequestsEndpoint

from . import constants
from .retry import retry

logger = logging.getLogger(__name__)

SESSIONS = threading.local()

CONNECT_TIMEOUT = 10 # in seconds
READ_TIMEOUT = 900 # in seconds


def get_url():
    url = os.getenv(constants.DISCOVERY_GRAPHQL_URL)
    if not url:
        raise RuntimeError(f'Missing Discovery GraphQL URL. Provide the Environment variable: {constants.DISCOVERY_GRAPHQL_URL}')
    return url


def get_requests_session():
    if not os.getenv(constants.ENABLE_DISCOVERY_RETRIES):
        return requests.Session()

    s = getattr(SESSIONS, 'session', None)
    if not s:
        SESSIONS.session = s = requests.Session()
        retries = Retry(
            total=10,
            backoff_factor=0.2,
            allowed_methods=None,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        s.mount('https://', HTTPAdapter(max_retries=retries))

    return s


def include_client_headers(headers):
    try:
        client_version = version('atlasai-discovery-client')
    except NameError:
        client_version = get_distribution('atlasai-discovery-client').version
    finally:
        headers['User-Agent'] = f'discovery-client/{client_version}'
        headers['X-Discovery-Client-Version'] = client_version


def get_endpoint(url, headers=None, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)):
    url = url or get_url()

    headers = headers or {}
    include_client_headers(headers)

    return RequestsEndpoint(
        url,
        base_headers=headers,
        timeout=timeout,
        session=get_requests_session(),
    )


@retry(attempts=10, backoff_factor=0.3)
def query(query, variables=None, url=None, headers=None):
    variables = variables or {}
    endpoint = get_endpoint(url, headers)
    include_authorization(endpoint.url, endpoint.base_headers)
    return endpoint(query, variables)

def get_secret_data(secret_id):
    try:
        from google.api_core.retry import Retry
        from google.cloud import secretmanager
    except ImportError:
        logger.warning('Client library not found: google-cloud-secret-manager')
        return None

    try:
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(
            request={
                'name': secret_id,
            },
            retry=Retry(),
        )
    except Exception as e:
        logger.error(f'Error getting data from Secret Manager: {secret_id} {e}')
        raise
    else:
        return response.payload.data.decode('utf-8')

def load_credentials(access_key=None, secret_key=None):
    access_key = access_key or os.getenv('DISCOVERY_ACCESS_KEY')
    secret_key = secret_key or os.getenv('DISCOVERY_SECRET_KEY')
    api_secret = os.getenv('DISCOVERY_API_SECRET')

    if not secret_key and api_secret:
        secret_key = get_secret_data(api_secret)
        if secret_key is not None:
            os.environ['DISCOVERY_SECRET_KEY'] = secret_key

    return access_key, secret_key


def include_authorization(url, headers, bearer_token=None, access_key=None, secret_key=None):
    bearer_token = bearer_token or os.getenv('DISCOVERY_BEARER_TOKEN')
    access_key, secret_key = load_credentials(
        access_key=access_key,
        secret_key=secret_key,
    )

    if bearer_token:
        headers['Authorization'] = f'Bearer {bearer_token}'
        return

    if not access_key and not secret_key:
        warnings.warn('No API Keys provided to access Discovery GraphQL. Provide the following: DISCOVERY_BEARER_TOKEN or the pair DISCOVERY_ACCESS_KEY and DISCOVERY_SECRET_KEY')
        return
    elif any([
        access_key is None,
        secret_key is None,
    ]):
        raise ValueError('DISCOVERY_ACCESS_KEY and DISCOVERY_SECRET_KEY must be provided together')

    product, version = 'discovery', '1'
    headers.update({
        'Host': urlparse(url).netloc,
        'X-Discovery-Date': arrow.utcnow().isoformat(),
        'X-Discovery-Credential': '/'.join([product, version, access_key]),
        'X-Discovery-SignedHeaders': 'x-discovery-date;x-discovery-credential;host',
    })

    sign_request(headers, secret_key)


def sign_request(headers, secret_key):
    product, version, access_key = headers['X-Discovery-Credential'].split('/')
    key = f'{product}{version}{secret_key}'.encode('utf-8')
    for msg in (
        headers['X-Discovery-Date'],
        f'{product}_{version}_request',
    ):
        obj = hmac.new(key, msg.encode('utf-8'), 'sha256')
        key = obj.digest()

    msg = '\n'.join([
        headers['X-Discovery-Date'],
        headers['X-Discovery-Credential'],
        headers['Host']
    ])
    headers['X-Discovery-Signature'] = hmac.new(key, msg.encode('utf-8'), 'sha256').hexdigest()
