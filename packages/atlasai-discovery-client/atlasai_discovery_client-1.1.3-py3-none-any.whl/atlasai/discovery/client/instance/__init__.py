"""
## CRUD operations on Instance
"""

from sgqlc.operation import Operation, select_depth

from . import parents
from .. import constants, endpoint, helpers, schema, utils
from ..misc import build_input_builder
from ..retry import enable_retry

__all__ = [
    'create',
    'get',
    'update',
    'delete',
    'search',
    'parents',
]

HELPERS = {
    'effective_date_range': helpers.encode_date_range,
    'tags': helpers.encode_tags,
    'reference': helpers.encode_json,
    'extent': helpers.encode_json,
    'assets': helpers.encode_assets,
    'parents': helpers.encode_str_list,
}

build_input = build_input_builder(HELPERS)

def create(product_id_or_name, assets, return_object=False, **kwargs):
    """
    Create an Instance for a Product

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.instance.create(product_id_or_name=<PRODUCT_ID_OR_NAME>, ...)
    ```

    Additional optional parameters include:

    * effective_date_range
    * ignore_timezone
    * tags
    * reference
    * assets
    * parents

    Returned object only consists of the Instance ID:

    ```python
    instance_id = response.create_instance.id
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.instance.create(
       ...:     '8dadcb06-7dc7-41c7-a522-70f307bd3cf9',
       ...:     effective_date_range='[2000-01-01T00:00:00Z, 2021-01-01T00:00:00Z)',
       ...:     ignore_timezone=True,
       ...:     tags='resolution:1000m,region:Africa',
       ...:     assets=[
       ...:         'gs://bucket/path/to/the/file.tif'
       ...:     ]
       ...: )

    In [3]: response.create_instance.id
    Out[3]: 'c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9'
    ```
    """

    input_ = build_input(
        schema.CreateInstanceInput,
        product_id_or_name=product_id_or_name,
        assets=assets,
        **kwargs
    )

    op = Operation(schema.Mutation)
    op.create_instance(input=input_).__fields__('id')

    response = op + endpoint.query(op)
    if return_object:
        return response.create_instance
    else:
        return response

def get(instance_id, return_object=False):
    """
    Get an Instance provided `id`

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.instance.get(<INSTANCE_ID>)
    ```

    Returned object is the Instance:

    ```python
    response.instance
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.instance.get('c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9')

    In [3]: response.instance
    Out[3]: Instance(id='c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9', product_id='8dadcb06-7dc7-41c7-a522-70f307bd3cf9', product_name='bborie.is.here.3', effective_date_range=DateRange(lower='2000-01-01T00:00:00+00:00', upper='2021-01-01T00:00:00+00:00', include_lower=True, include_upper=False, empty=False), ignore_timezone=True, tags=[Tag(name='region', value='Africa'), Tag(name='resolution', value='1000m')], reference='{}', extent=None, assets=[Asset(id='8ba178d3-e6c7-42db-a334-0489b43e4faa', instance_id='c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9', type='Unknown', path='gs://bucket/path/to/the/file.tif', metadata='{}', crs=None, extent=None)], parents=[])
    ```
    """

    op = Operation(schema.Query)
    op.instance(id=instance_id)

    with enable_retry(), select_depth(3):
        response = op + endpoint.query(op)
        if return_object:
            return response.instance
        else:
            return response

def update(instance_id, return_object=False, **kwargs):
    """
    Update an Instance provided `id`

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.instance.update(
      instance_id=<INSTANCE_ID>,
      ...
    )
    ```

    Additional optional parameters include:

    * effective_date_range
    * ignore_timezone
    * tags
    * reference
    * assets
    * parents

    Returned object only consists of the Instance ID

    ```python
    instance_id = response.update_instance.id
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.instance.update(
       ...:   'c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9',
       ...:   assets=[ # note that this REPLACES all existing assets
       ...:     {
       ...:       'path': 'gs://bucket/path/to/the/file',
       ...:       'tags': 'key:value',
       ...:     },
       ...:   ],
       ...:   tags="year:2020,key:value',
       ...: )

    In [3]: response.update_instance.id
    Out[3]: 'c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9'
    ```
    """

    input_ = build_input(schema.UpdateInstanceInput, **kwargs)

    op = Operation(schema.Mutation)
    op.update_instance(id=instance_id, input=input_).__fields__('id')

    response = op + endpoint.query(op)
    if return_object:
        return response.update_instance
    else:
        return response

def delete(instance_id, return_object=False):
    """
    Delete an Instance provided `id`

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.instance.delete(instance_id=<INSTANCE_ID>)
    ```

    Returned object is the deleted Instance:

    ```python
    response.instance
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.instance.delete('c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9')

    In [3]: response.delete_instance
    Out[3]: Instance(id='c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9', product_id='8dadcb06-7dc7-41c7-a522-70f307bd3cf9', product_name='bborie.is.here.3', effective_date_range=DateRange(lower='2000-01-01T00:00:00+00:00', upper='2021-01-01T00:00:00+00:00', include_lower=True, include_upper=False, empty=False), ignore_timezone=True, tags=[Tag(name='region', value='Africa'), Tag(name='resolution', value='1000m')], reference='{}', extent=None, assets=[Asset(id='8ba178d3-e6c7-42db-a334-0489b43e4faa', instance_id='c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9', type='Unknown', path='gs://bucket/path/to/the/file.tif', metadata='{}', crs=None, extent=None)], parents=[])
    ```
    """

    op = Operation(schema.Mutation)
    op.delete_instance(
        id=instance_id,
    ).__fields__('id')

    response = op + endpoint.query(op)
    if return_object:
        return response.delete_instance
    else:
        return response

def _search(
    odata=None,
    limit=constants.DEFAULT_PAGE_SIZE,
    offset=constants.DEFAULT_OFFSET,
    order_by=None,
    filter_children=False,
):
    input_ = helpers.search_build_input(
        schema.BasicSearchInput,
        odata=odata,
        limit=limit,
        offset=offset,
        order_by=order_by,
        filter_children=filter_children,
    )

    with enable_retry(), select_depth(5):
        op = Operation(schema.Query)
        op.instances(input=input_).__fields__()

        return op + endpoint.query(op)

def search(
    odata=None,
    limit=constants.DEFAULT_PAGE_SIZE,
    offset=constants.DEFAULT_OFFSET,
    order_by=None,
    paginator=False,
    filter_assets=False,
):
    """
    Full-text and OData search for Instances

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.instance.search(...)
    ```

    Additional optional parameters include:

    * odata
    * limit
    * offset
    * paginator
    * filter_assets

    Returned object is a paginated set of matching Instances:

    ```python
    response.instances.results
    ```

    #### OData

    Available columns to filter upon for Instance Search include:

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
    from atlasai.discovery import client
    response = client.instance.search(odata='''
      contains(instance.effective_date_range, 2022-01-01T00:00:00Z) and
      startswith(product.internal_name, 'atlasai.') and
      asset.type eq 'Raster'
    ''')
    ```

    #### Example #2

    ```python
    from atlasai.discovery import client
    response = client.instance.search(odata='''
      product.internal_name eq 'esa.sentinel2.l1c' and
      overlaps(instance.effective_date_range, '[2022-01-01T00:00:00Z,2022-01-02T00:00:00Z)') and
      extract_path(instance.tags, ('cloud_cover'), 'float') le 20.0
    ''')
    ```

    #### Example #3

    By setting `filter_assets=True` and specifying an Asset filter, the
    returned Instances will only have Assets where the filter applies

    ```python
    from atlasai.discovery import client
    response = client.instance.search(
        odata='''
            product.internal_name eq 'usda.naip' and
            overlaps(instance.effective_date_range, '[2022-01-01T00:00:00Z,2022-01-02T00:00:00Z)') and
            contains(asset.tags, '{"mgrs_tile": "06071"}')
        ''',
        filter_assets=True,
    )
    ```
    """

    kwargs = dict(
        odata=odata,
        limit=limit,
        offset=offset,
        order_by=order_by,
        filter_children=filter_assets,
    )

    if paginator:
        return utils.paginator(_search, **kwargs)
    else:
        return _search(**kwargs)
