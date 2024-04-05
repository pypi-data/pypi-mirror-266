"""
## Helpers for managing Instances part of a Release
"""

from sgqlc.operation import Operation

from .. import endpoint, helpers, schema
from ..misc import build_input_builder

__all__ = [
    'add',
    'remove',
]

HELPERS = {
    'instance_ids': helpers.encode_str_list,
}
build_input = build_input_builder(HELPERS)

def add(release_id, *instance_ids):
    """
    Add Instances to this Release

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.release.instances.add(
      <RELEASE_ID>,
      <INSTANCE_ID>,
      ...
      <INSTANCE_ID>,
    )
    ```

    Returned object only consists of the Release ID

    ```python
    release_id = response.update_release.id
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.release.instances.add(
       ...:   '51cd265d-8680-413e-88f4-234e2b1c317c',
       ...:   '053de543-d0a0-4c71-aae2-2f78e8813d90', # Instance ID
       ...:   'e750aacc-c72b-44c2-b88c-b2e1e012a2eb', # Instance ID
       ...:   'bc28e4ff-89d2-437b-a437-095a69d337cd', # Instance ID
       ...: )

    In [3]: response.update_release.id
    Out[3]: '51cd265d-8680-413e-88f4-234e2b1c317c'
    ```
    """

    input_ = build_input(
        schema.UpdateReleaseInput,
        instance_ids=instance_ids,
        instance_ids_action='Add',
    )

    op = Operation(schema.Mutation)
    op.update_release(id=release_id, input=input_).__fields__('id')

    return op + endpoint.query(op)

def remove(release_id, *instance_ids):
    """
    Remove Instances from this Release

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.release.instances.remove(
      <RELEASE_ID>,
      <INSTANCE_ID>,
      ...
      <INSTANCE_ID>,
    )
    ```

    Returned object only consists of the Release ID

    ```python
    release_id = response.update_release.id
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: response = client.release.instances.remove(
       ...:   '51cd265d-8680-413e-88f4-234e2b1c317c',
       ...:   '053de543-d0a0-4c71-aae2-2f78e8813d90', # Instance ID
       ...:   'e750aacc-c72b-44c2-b88c-b2e1e012a2eb', # Instance ID
       ...:   'bc28e4ff-89d2-437b-a437-095a69d337cd', # Instance ID
       ...: )

    In [3]: response.update_release.id
    Out[3]: '51cd265d-8680-413e-88f4-234e2b1c317c'
    ```
    """

    input_ = build_input(
        schema.UpdateReleaseInput,
        instance_ids=instance_ids,
        instance_ids_action='Delete',
    )

    op = Operation(schema.Mutation)
    op.update_release(id=release_id, input=input_).__fields__('id')

    return op + endpoint.query(op)
