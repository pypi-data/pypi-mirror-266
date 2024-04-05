"""
## Helpers for managing Instance parents
"""

from sgqlc.operation import Operation
from .. import endpoint, helpers, schema
from ..misc import build_input_builder

__all__ = [
    'add',
    'remove',
]

HELPERS = {
    'parents': helpers.encode_str_list,
}
build_input = build_input_builder(HELPERS)

def add(instance_id, *parent_ids):
    """
    Add Instances as parents of this Instance

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.instance.parents.add(
      <INSTANCE_ID>,
      <PARENT_INSTANCE_ID>,
      ...
      <PARENT_INSTANCE_ID>,
    )
    ```

    Returned object only consists of the Instance ID

    ```python
    instance_id = response.update_instance.id
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.instance.parents.add(
       ...:   'c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9',
       ...:   '053de543-d0a0-4c71-aae2-2f78e8813d90', # parent Instance ID
       ...:   'e750aacc-c72b-44c2-b88c-b2e1e012a2eb', # parent Instance ID
       ...:   'bc28e4ff-89d2-437b-a437-095a69d337cd', # parent Instance ID
       ...: )

    In [3]: response.update_instance.id
    Out[3]: 'c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9'
    ```
    """

    input_ = build_input(
        schema.UpdateInstanceInput,
        parents=parent_ids,
        parents_action='Add',
    )

    op = Operation(schema.Mutation)
    op.update_instance(id=instance_id, input=input_).__fields__('id')

    return op + endpoint.query(op)

def remove(instance_id, *parent_ids):
    """
    Remove Instances as parents from this Instance

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.instance.parents.remove(
      <INSTANCE_ID>,
      <PARENT_INSTANCE_ID>,
      ...
      <PARENT_INSTANCE_ID>,
    )
    ```

    Returned object only consists of the Instance ID

    ```python
    instance_id = response.update_instance.id
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.instance.parents.remove(
       ...:   'c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9',
       ...:   '053de543-d0a0-4c71-aae2-2f78e8813d90', # parent Instance ID
       ...:   'e750aacc-c72b-44c2-b88c-b2e1e012a2eb', # parent Instance ID
       ...:   'bc28e4ff-89d2-437b-a437-095a69d337cd', # parent Instance ID
       ...: )

    In [3]: response.update_instance.id
    Out[3]: 'c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9'
    ```
    """

    input_ = build_input(
        schema.UpdateInstanceInput,
        parents=parent_ids,
        parents_action='Delete',
    )

    op = Operation(schema.Mutation)
    op.update_instance(id=instance_id, input=input_).__fields__('id')

    return op + endpoint.query(op)
