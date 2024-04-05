"""
## Other Operations
"""
import os

from furl import furl
import requests
from sgqlc.operation import Operation, select_depth

from . import endpoint, helpers, schema, utils
from .misc import build_input_builder
from .retry import enable_retry

__all__ = [
    'distinct',
    'entities',
    'search',
    'authenticate',
    'get_download_uris',
]

distinct_build_input = build_input_builder()


def distinct(entity, **kwargs):
    """
    Get a list of distinct (i.e. unique) objects of `entity`

    Valid entities are:

        * product
        * instance
        * release

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.distinct(<ENTITY>)
    ```
    """

    input_ = distinct_build_input(
        schema.DistinctInput,
        entity=entity,
        **kwargs
    )

    with select_depth(2):
        op = Operation(schema.Query)
        op.distinct(input=input_).__fields__()

        return op + endpoint.query(op)


def entities(context=None):
    """
    Get a list of supported OData entities for the specified `context`

    Valid contexts are:

        * Search (default)
        * Product
        * Instance
        * Release

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.entities(<CONTEXT>)
    ```
    """

    context = context or 'Search'
    op = Operation(schema.Query)
    op.entities(context=context)

    return op + endpoint.query(op)

def _search(**kwargs):
    input_ = helpers.search_build_input(
        schema.SearchInput,
        **kwargs
    )

    with select_depth(5):
        op = Operation(schema.Query)
        op.search(input=input_).__fields__()

        return op + endpoint.query(op)

def search(paginator=False, **kwargs):
    """
    Discovery Search across all Products, Instances, Releases and Assets

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.search(...)
    ```

    Additional optional parameters include:

    * odata
    * limit
    * offset
    * complete_products
    * paginator

    Returned object is a paginated set of matching results:

    ```python
    response.search.results
    ```

    #### OData

    Available columns to filter upon for Discovery Search include:

    * instance.create_date
    * instance.delete_date
    * instance.deleted
    * instance.effective_date_range
    * instance.extent
    * instance.id
    * instance.ignore_timezone
    * instance.modify_date
    * instance.product_id
    * instance.reference
    * instance.tags
    * instance.tsvector
    * product.create_date
    * product.data_steward
    * product.delete_date
    * product.deleted
    * product.description
    * product.display_name
    * product.id
    * product.internal_name
    * product.license
    * product.modify_date
    * product.reference
    * product.tags
    * product.tsvector
    * release.audience
    * release.create_date
    * release.delete_date
    * release.deleted
    * release.description
    * release.id
    * release.license
    * release.modify_date
    * release.product_id
    * release.publish_status
    * release.tags
    * release.tsvector
    * release.version

    #### Example #1

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.search(complete_products=True, limit=10, offset=0)

    In [3]: response.search.results
    Out[3]:
    [
    FullSearchResult(product=Product(id='ca3e2e8a-e5a7-4a53-b951-499b258e26a4', internal_name='a.b.c', display_name=None, description='foobar', license=None, reference='{}', data_steward='{}', tags=[], releases=[Release(id='26f1433a-0e9b-4b65-a75a-73084afa6fb6', product_id='ca3e2e8a-e5a7-4a53-b951-499b258e26a4', instance_ids=[], version='0.0.1', description=None, publish_status='NotPublished', license=None, audience='{}')]), instances=[Instance(id='a580f9ab-ab73-458c-9b0c-cfcd538a863a', product_id='ca3e2e8a-e5a7-4a53-b951-499b258e26a4', product_name='a.b.c', effective_date_range=DateRange(lower='2000-01-01T00:00:00+00:00', upper='2010-01-01T00:00:00+00:00', include_lower=True, include_upper=False, empty=False), ignore_timezone=True, tags=[], reference='{}', extent=None, assets=[Asset(id='5a880ca8-575f-4a8c-9baf-a3c0bd32079c', instance_id='a580f9ab-ab73-458c-9b0c-cfcd538a863a', type='Unknown', path='gs://anotherbucket/for/the/win', metadata='{}', crs=None, extent=None)], parents=[])]),
     FullSearchResult(product=Product(id='482951a1-660f-4c14-9596-fe3e0a15d6fd', internal_name='a.b.c.d', display_name=None, description=None, license=None, reference='{}', data_steward='{}', tags=[], releases=[]), instances=[]),
    ...
     FullSearchResult(product=Product(id='6061ab44-dfea-4204-ae7e-a302e7055c73', internal_name='foo.bar.baz.quz', display_name=None, description=None, license=None, reference='{}', data_steward='{}', tags=[], releases=[]), instances=[])
    ]
    ```

    #### Example #2

    ```python
    from atlasai.discovery import client
    response = client.search(odata='''
      overlaps(instance.effective_date_range, '[2022-01-01T00:00:00Z,)') and
      startswith(product.internal_name, 'atlasai.') and
      release.version ge '1.0.0'
    ''')
    ```

    #### Example #3

    ```python
    from atlasai.discovery import client
    response = client.search(odata='''
      product.internal_name eq 'esa.sentinel2.l1c' and
      overlaps(instance.effective_date_range, '[2022-01-01T00:00:00Z,2022-01-02T00:00:00Z)') and
      extract_path(instance.tags, ('cloud_cover'), 'float') le 20.0 and
      extract_path(asset.tags, ('type'), 'text') eq 'data'
    ''')
    ```
    """
    return utils.paginator(_search, **kwargs)

def authenticate(env_name=None):
    """
    Authenticate with Discovery

    Returns an OAuth2 Access Token

    If `env_name` provided, the Access Token will be saved
    to the named environment variable

    #### Usage

    ```python
    from atlasai.discovery import client

    token = client.authenticate(<OPTIONAL_ENV_VARIABLE_NAME>)
    ```
    """

    f = furl(endpoint.get_url())
    f.path = 'token'
    url = f.url
    headers = {}
    endpoint.include_authorization(url, headers)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    token = data['access_token']

    if env_name:
        os.environ[env_name] = token

    user_id = data.get('email') or data.get('sub') or 'AtlasAI Employee'
    os.environ['LOGNAME'] = user_id

    return token

def get_download_uris(reference, return_object=True):
    """
    Get signed URIs for Assets for Discovery Reference provided
    Signed URIs expire 48 hours after the URIs are created

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.get_download_uris(reference=<DISCOVERY_REFERENCE>)
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.get_download_uris(reference=<DISCOVERY_REFERENCE>)

    In [3]: response
    Out[3]:
    ['https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/49/P/DN/...',
      ...,
     'https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/49/P/DN/...']
    ```
    """

    op = Operation(schema.Query)
    op.download(reference=reference)

    with enable_retry():
        response = op + endpoint.query(op)

        if return_object:
            return response.download
        else:
            return response
