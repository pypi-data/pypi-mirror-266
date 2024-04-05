"""
## CRUD operations on Release
"""

from sgqlc.operation import Operation, select_depth

from . import instances
from .. import constants, endpoint, helpers, schema, utils
from ..misc import build_input_builder
from ..retry import enable_retry
from ..schema import PublicationStatus

__all__ = [
    'create',
    'get',
    'update',
    'delete',
    'search',
    'instances',
]

HELPERS = {
    'instance_ids': helpers.encode_str_list,
    'version': helpers.encode_semver,
    'publish_status': helpers.in_(PublicationStatus),
    'tags': helpers.encode_tags,
    'audience': helpers.encode_json,
}

build_input = build_input_builder(HELPERS)

def create(product_id_or_name, return_object=False, **kwargs):
    """
    Create a Release for a Product

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.release.create(product_id_or_name=<PRODUCT_ID_OR_NAME>, ...)
    ```

    Additional optional parameters include:

    * instance_ids
    * version
    * description
    * publis_status
    * license
    * tags
    * audience

    Returned object only consists of the Release ID:

    ```python
    release_id = response.create_release.id
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.release.create(
       ...:     '8dadcb06-7dc7-41c7-a522-70f307bd3cf9',
       ...:     instance_ids=['c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9'],
       ...:     version='0.0.1',
       ...:     description='this is a release',
       ...:     publish_status='NotPublished',
       ...:     tags='resolution:1000m,region:Africa',
       ...: )

    In [3]: response.create_release.id
    Out[3]: '51cd265d-8680-413e-88f4-234e2b1c317c'
    ```
    """
    input_ = build_input(
        schema.CreateReleaseInput,
        product_id_or_name=product_id_or_name,
        **kwargs
    )

    op = Operation(schema.Mutation)
    op.create_release(input=input_).__fields__('id')

    response = op + endpoint.query(op)
    if return_object:
        return response.create_release
    else:
        return response

def get(release_id, return_object=False):
    """
    Get a Release provided `id`

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.release.get(<RELEASE_ID>)
    ```

    Returned object is the Release:

    ```python
    response.release
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.release.get('51cd265d-8680-413e-88f4-234e2b1c317c')

    In [3]: response.release
    Out[3]: Release(id='51cd265d-8680-413e-88f4-234e2b1c317c', product_id='8dadcb06-7dc7-41c7-a522-70f307bd3cf9', instance_ids=['c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9'], version='0.0.1', description='this is a release', publish_status='NotPublished', license=None, tags=[Tag(name='region', value='Africa'), Tag(name='resolution', value='1000m')], audience='{}')
    ```
    """

    op = Operation(schema.Query)
    op.release(id=release_id)

    with enable_retry():
        response = op + endpoint.query(op)
        if return_object:
            return response.release
        else:
            return response

def update(release_id, return_object=False, **kwargs):
    """
    Update an Release provided `id`

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.release.update(
      release_id=<RELEASE_ID>,
      ...
    )
    ```

    Additional optional parameters include:

    * version
    * description
    * publish_status
    * license
    * tags
    * audience
    * instance_ids

    Returned object only consists of the Release ID

    ```python
    release_id = response.update_release.id
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.release.update(
       ...:   '51cd265d-8680-413e-88f4-234e2b1c317c',
       ...:   tags="year:2020,key:value',
       ...: )

    In [3]: response.update_release.id
    Out[3]: '51cd265d-8680-413e-88f4-234e2b1c317c'
    ```
    """

    input_ = build_input(schema.UpdateReleaseInput, **kwargs)

    op = Operation(schema.Mutation)
    op.update_release(
        id=release_id,
        input=input_
    ).__fields__('id')

    response = op + endpoint.query(op)
    if return_object:
        return response.update_release
    else:
        return response

def delete(release_id, return_object=False):
    """
    Delete a Release provided `id`

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.release.delete(release_id=<RELEASE_ID>)
    ```

    Returned object is the deleted Release:

    ```python
    response.release
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.release.delete('51cd265d-8680-413e-88f4-234e2b1c317c')

    In [3]: response.delete_release
    Out[3]: Release(id='51cd265d-8680-413e-88f4-234e2b1c317c', product_id='8dadcb06-7dc7-41c7-a522-70f307bd3cf9', instance_ids=['c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9'], version='0.0.1', description='this is a release', publish_status='NotPublished', license=None, tags=[Tag(name='region', value='Africa'), Tag(name='resolution', value='1000m')], audience='{}')
    ```
    """

    op = Operation(schema.Mutation)
    op.delete_release(
        id=release_id,
    ).__fields__('id')

    response = op + endpoint.query(op)
    if return_object:
        return response.delete_release
    else:
        return response

def _search(
    odata=None,
    limit=constants.DEFAULT_PAGE_SIZE,
    offset=constants.DEFAULT_OFFSET,
    order_by=None,
):
    input_ = helpers.search_build_input(
        schema.BasicSearchInput,
        odata=odata,
        limit=limit,
        offset=offset,
        order_by=order_by,
    )

    with enable_retry(), select_depth(5):
        op = Operation(schema.Query)
        op.releases(input=input_).__fields__()

        return op + endpoint.query(op)

def search(
    odata=None,
    limit=constants.DEFAULT_PAGE_SIZE,
    offset=constants.DEFAULT_OFFSET,
    order_by=None,
    paginator=False,
):
    """
    Full-text and OData search for Releases

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.release.search(...)
    ```

    Additional optional parameters include:

    * odata
    * limit
    * offset
    * paginator

    Returned object is a paginated set of matching Releases:

    ```python
    response.releases.results
    ```

    #### OData

    Available columns to filter upon for Release Search include:

    * asset.create_date
    * asset.crs
    * asset.delete_date
    * asset.deleted
    * asset.extent
    * asset.id
    * asset.instance_id
    * asset.metadata_
    * asset.modify_date
    * asset.path
    * asset.tags
    * asset.tsvector
    * asset.type
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

    #### Example #1

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.release.search('bborie')

    In [3]: response.releases.results
    Out[3]:
    [
    Release(__typename__='Release', id='d99bb5f4-5e89-4acc-87a3-6b2fdec6912e', product_id='83214a4e-a6af-4d70-a7f5-e12c5f26d458', instance_ids=[], version='0.0.1', description=None, publish_status='InReview', license=None, tags=[], audience='{}'),
     Release(__typename__='Release', id='51cd265d-8680-413e-88f4-234e2b1c317c', product_id='8dadcb06-7dc7-41c7-a522-70f307bd3cf9', instance_ids=['c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9'], version='0.0.1', description='this is a release', publish_status='NotPublished', license=None, tags=[Tag(name='region', value='Africa'), Tag(name='resolution', value='1000m')], audience='{}')
    ]
    ```

    #### Example #2

    ```python
    from atlasai.discovery import client
    response = client.release.search(odata='''
      contains(instance.effective_date_range, 2022-01-01T00:00:00Z) and
      startswith(product.internal_name, 'atlasai.') and
      release.version ge '1.0.0' and
      release.version lt '2.0.0'
    ''')
    ```
    """

    kwargs = dict(
        odata=odata,
        limit=limit,
        offset=offset,
        order_by=order_by,
    )

    if paginator:
        return utils.paginator(_search, **kwargs)
    else:
        return _search(**kwargs)
