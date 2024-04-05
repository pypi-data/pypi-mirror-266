"""
## Bulk operations on Instances
"""

from sgqlc.operation import Operation

from . import endpoint, misc, schema
from .instance import build_input, search

__all__ = [
    'create',
    'get',
    'update',
    'delete',
]

CreateInput = misc.build_namespace_input(schema.CreateInstanceInput)
UpdateInput = misc.build_namespace_input(schema.UpdateInstanceInputWithId)

def create(*inputs, return_objects=False):
    """
    Bulk create Instances. Each Instance can be expressed as either a `CreateInput` object or a python dictionary

    #### Usage

    Using `CreateInput`

    ```python
    from atlasai.discovery import client

    response = client.instances.create(
      client.instances.CreateInput(
        product_id_or_name=<PRODUCT_ID_OR_NAME>,
        ...
      ),
      ...
      client.instances.CreateInput(
        product_id_or_name=<PRODUCT_ID_OR_NAME>,
        ...
      ),
    )
    ```

    or using dictionaries

    ```python
    from atlasai.discovery import client

    response = client.instances.create(
      {
        "product_id_or_name": <PRODUCT_ID_OR_NAME>,
        ...
      },
      ...
      {
        "product_id_or_name": <PRODUCT_ID_OR_NAME>,
        ...
      },
    )
    ```
    """

    _inputs = [
        build_input(
            schema.CreateInstanceInput,
            **misc.input_as_dict(input_)
        )
        for input_ in inputs
    ]

    op = Operation(schema.Mutation)
    op.create_instances(inputs=_inputs).__fields__('id')

    response = op + endpoint.query(op)
    if return_objects:
        return response.create_instances
    else:
        return response

def get(*instance_ids, **kwargs):
    """
    Get Instances provided one or more `id`

    This is just a thin wrapper around `client.instance.search()`

    #### Usage

    ```python
    from atlasai.discovery import client

    instances = client.instances.get(<INSTANCE_ID>, <INSTANCE_ID>, ..., <INSTANCE_ID>)
    ```

    Returned object is a paginator to be looped through

    ```python
    for instance in instances:
        instance.id
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: instances = disco.instances.get('adb507d2-2d60-47b7-9414-f85af59da7f8','089167de-92b0-42a4-9a94-f87b34c03724')

    In [3]: for instance in instances:
       ...:     print(instance.id)
       ...:
    089167de-92b0-42a4-9a94-f87b34c03724
    adb507d2-2d60-47b7-9414-f85af59da7f8
    ```
    """

    if len(instance_ids) < 1:
        raise ValueError('At least one Instance ID must be provided')
    elif len(instance_ids) < 2:
        odata = f'''
instance.id eq '{instance_ids[0]}'
        '''
    else:
        ids = "','".join(instance_ids)
        odata = f'''
instance.id in ('{ids}')
        '''

    return search(odata=odata, paginator=True)

def update(*inputs, return_objects=False):
    """
    Bulk update Instances. Each Instance can be expressed as either a `UpdateInput` object or a python dictionary

    #### Usage

    Using `UpdateInput`

    ```python
    from atlasai.discovery import client

    response = client.instances.update(
      client.instances.UpdateInput(
        id=<INSTANCE_ID>,
        ...
      ),
      ...
      client.instances.UpdateInput(
        id=<INSTANCE_ID>,
        ...
      ),
    )
    ```

    or using dictionaries

    ```python
    from atlasai.discovery import client

    response = client.instances.update(
      {
        "id": <INSTANCE_ID>,
        ...
      },
      ...
      {
        "id": <INSTANCE_ID>,
        ...
      },
    )
    ```
    """

    _inputs = [
        build_input(
            schema.UpdateInstanceInputWithId,
            **misc.input_as_dict(input_)
        )
        for input_ in inputs
    ]

    op = Operation(schema.Mutation)
    op.update_instances(inputs=_inputs).__fields__('id')

    response = op + endpoint.query(op)
    if return_objects:
        return response.update_instances
    else:
        return response

def delete(*ids, return_objects=False):
    """
    Bulk delete Instances by providing `id`

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.instances.delete(<INSTANCE_ID>, ...)
    ```
    """

    op = Operation(schema.Mutation)
    op.delete_instances(
        ids=ids,
    ).__fields__('id')

    response = op + endpoint.query(op)
    if return_objects:
        return response.delete_instances
    else:
        return response
