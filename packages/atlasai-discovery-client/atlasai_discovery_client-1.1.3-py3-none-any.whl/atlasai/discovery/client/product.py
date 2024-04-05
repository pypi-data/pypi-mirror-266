"""
## CRUD operations on Product
"""

from sgqlc.operation import Operation, select_depth

from . import constants, endpoint, helpers, schema, utils
from .misc import build_input_builder
from .retry import enable_retry

__all__ = [
    'create',
    'get',
    'update',
    'delete',
    'search',
]

HELPERS = {
    'reference': helpers.encode_json,
    'data_steward': helpers.encode_json,
    'tags': helpers.encode_tags,
}

build_input = build_input_builder(HELPERS)

def create(product_name, return_object=False, **kwargs):
    """
    Create Product with provided `internal_name`

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.product.create(product_name=<INTERNAL_NAME>, ...)
    ```

    Additional optional parameters include:

    * display_name
    * description
    * license
    * reference
    * data_steward
    * tags

    Returned object consists only of the Product ID:

    ```python
    product_id = response.create_product.id
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.product.create(
       ...:   product_name='atlasai.africa.awi.1000m',
       ...:   displayName='Friendly name such as: AWI for Africa at 1000m resolution',
       ...:   description='I am a description',
       ...:   tags={
       ...:     'year': '2020',
       ...:   },
       ...: )

    In [3]: response.create_product.id
    Out[3]: '8dadcb06-7dc7-41c7-a522-70f307bd3cf9'
    ```
    """

    input_ = build_input(
        schema.CreateProductInput,
        internal_name=product_name,
        **kwargs
    )

    op = Operation(schema.Mutation)
    op.create_product(input=input_).__fields__('id')

    response = op + endpoint.query(op)
    if return_object:
        return response.create_product
    else:
        return response

def get(product_id_or_name, return_object=False):
    """
    Get a Product provided `id` or `internal_name`

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.product.get(<PRODUCT_ID_OR_NAME>)
    ```

    Returned object is the Product:

    ```python
    response.product
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.product.get('8dadcb06-7dc7-41c7-a522-70f307bd3cf9')

    In [3]: response.product
    Out[3]: Product(id='8dadcb06-7dc7-41c7-a522-70f307bd3cf9', internal_name='bborie.is.here.3', display_name=None, description=None, license=None, reference='{"test": "test"}', data_steward='{}', tags=[Tag(name='bar', value='baz'), Tag(name='foo', value='bar')], releases=[])
    ```
    """

    op = Operation(schema.Query)
    op.product(id=product_id_or_name)

    with enable_retry():
        response = op + endpoint.query(op)
        if return_object:
            return response.product
        else:
            return response

def update(product_id_or_name, return_object=False, **kwargs):
    """
    Update a Product provided `id` or `internal_name`

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.product.update(
      <PRODUCT_ID_OR_NAME>,
      ...
    )
    ```

    Additional optional parameters include:

    * internal_name
    * display_name
    * description
    * license
    * reference
    * data_steward
    * tags

    Returned object consists only of the Product ID:

    ```python
    product_id = response.update_product.id
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.product.update(
       ...:   '8dadcb06-7dc7-41c7-a522-70f307bd3cf9',
       ...:   displayName='Friendly name such as: AWI for Africa at 1000m resolution'
       ...:   description='I am a description',
       ...:   tags="year:2020,key:value',
       ...: )

    In [3]: response.update_product.id
    Out[3]: '8dadcb06-7dc7-41c7-a522-70f307bd3cf9'
    ```
    """

    input_ = build_input(schema.UpdateProductInput, **kwargs)

    op = Operation(schema.Mutation)
    op.update_product(id=product_id_or_name, input=input_).__fields__('id')

    response = op + endpoint.query(op)
    if return_object:
        return response.update_product
    else:
        return response

def delete(product_id_or_name, return_object=False):
    """
    Delete a Product provided `id` or `internal_name`

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.product.delete(<PRODUCT_ID_OR_NAME>)
    ```

    Returned object is the deleted Product:

    ```python
    response.product
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.product.delete('8dadcb06-7dc7-41c7-a522-70f307bd3cf9')

    In [3]: response.delete_product
    Out[3]: Product(id='8dadcb06-7dc7-41c7-a522-70f307bd3cf9', internal_name='bborie.is.here.3', display_name=None, description=None, license=None, reference='{"test": "test"}', data_steward='{}', tags=[Tag(name='bar', value='baz'), Tag(name='foo', value='bar')], releases=[])
    ```
    """

    op = Operation(schema.Mutation)
    op.delete_product(
        id=product_id_or_name,
    ).__fields__('id')

    response = op + endpoint.query(op)
    if return_object:
        return response.delete_product
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
        op.products(input=input_).__fields__()

        return op + endpoint.query(op)

def search(
    odata=None,
    limit=constants.DEFAULT_PAGE_SIZE,
    offset=constants.DEFAULT_OFFSET,
    order_by=None,
    paginator=False,
):
    """
    Full-text and OData search for Products

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.product.search(...)
    ```

    Additional optional parameters include:

    * odata
    * limit
    * offset
    * paginator

    Returned object is a paginated set of matching Products:

    ```python
    response.products.results
    ```

    #### OData

    Available columns to filter upon for Product Search include:

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

    Search for Products where an Instance's extent spatially intersects the provided geometry. Geometry provided MUST be in WGS84. Geometry can either be a WKT or a GeoJSON

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.product.search(
      odata='''
    st_intersects(instance.extent, 'POINT(36.81681924130423 -1.246244861550351)')
    ''')

    In [3]: response = client.product.search(
      odata='''
    st_intersects(instance.extent, '{"type": "Point", "coordinates": [36.81681924130423, -1.246244861550351]}')
    ''')
    ```

    #### Example #2

    Search for Products with the Tag. Use `exists()` for presence of a Tag. Use `contains()` for Tag of specific value

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.product.search(
      odata='''
    exists(product.tags, 'region')
    ''')

    In [3]: response = client.product.search(
      odata='''
    contains(product.tags, '{"region": "Africa"}')
    ''')
    ```

    #### Example #3

    Compound OData

    ```python
    from atlasai.discovery import client
    response = client.product.search(odata='''
      contains(instance.effective_date_range, 2022-01-01T00:00:00Z) and
      startswith(product.internal_name, 'atlasai.') and
      release.version ge '1.0.0'
    ''')
    ```

    #### Example #4

    Instead of search results, return a paginator to iterate through each returned Product

    ```python
    from atlasai.discovery import client
    products = client.product.search(odata='''
            contains(instance.effective_date_range, 2022-01-01T00:00:00Z) and
            startswith(product.internal_name, 'atlasai.') and
            release.version ge '1.0.0'
        ''',
        paginator=True,
    )

    for product in products:
        print(product.id)
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
