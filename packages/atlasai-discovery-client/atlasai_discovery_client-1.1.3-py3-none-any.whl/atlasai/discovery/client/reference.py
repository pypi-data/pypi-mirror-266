"""
## Operations on Discovery Reference

A Discovery Reference is a string with the following format:

```
discovery/PATH/FOR/OBJECT
```

### Example Discovery References

#### Product by `id`

```
discovery/product/83214a4e-a6af-4d70-a7f5-e12c5f26d458
```

#### Product by `internal_name`

```
discovery/product/atlasai.africa.awi.1000m
```

#### Instance

```
discovery/instance/c3b8ffd8-1e19-47c6-b3f5-1d7ccfdb99e9
```

#### Release

```
discovery/release/d99bb5f4-5e89-4acc-87a3-6b2fdec6912e
```

#### Product Release by version

```
discovery/product/83214a4e-a6af-4d70-a7f5-e12c5f26d458/release/0.0.1
```

#### Latest Product Release

```
discovery/product/83214a4e-a6af-4d70-a7f5-e12c5f26d458/release/latest
```
"""

from furl import furl

from . import endpoint
from .namespace import RecursiveNamespace
from .retry import enable_retry

def get(reference, return_object=False):
    """
    Get the details of an object provided a reference (e.g. provided a Product reference, Product details will be returned)

    #### Usage

    ```python
    from atlasai.discovery import client

    response = client.reference.get(<REFERENCE>)
    ```

    The response for a Reference *IS* different than that of any other Discovery Client API

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: client.reference.get('discovery/release/6d5ac0ca-b56c-4e5e-84c9-4f367339f562')
    Out[2]:
    namespace(__typename='FullSearchResult',
              product=namespace(__typename='Product',
                                id='08829220-d2a4-4b9c-8e5a-795792eef606',
                                internal_name='SPAM.Global.Arabica_Coffee.Physical_Area.Complete_Crop.2005.3-2-0',
                                display_name=None,
                                description=None,
                                license=None,
                                reference=namespace(),
                                data_steward=namespace(),
                                tags=[namespace(name='year', value=2005),
                                ...

    In [3]: response.product
    Out[3]:
    namespace(__typename='Product',
              id='08829220-d2a4-4b9c-8e5a-795792eef606',
              internal_name='SPAM.Global.Arabica_Coffee.Physical_Area.Complete_Crop.2005.3-2-0',
              display_name=None,
              description=None,
              ...
    ```
    """

    f = furl(endpoint.get_url())
    f.path = (
        reference[1:]
        if reference[0] == '/'
        else reference
    )
    url = f.url
    headers = {}
    endpoint.include_authorization(url, headers)

    with enable_retry():
        session = endpoint.get_requests_session()
        response = session.get(url, headers=headers)
        response.raise_for_status()

    return RecursiveNamespace(**(response.json()))
