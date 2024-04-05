def paginate(fn, *args, **kwargs):
    """
    Helper function for handling paginated responses

    Given that all search methods (e.g. `product.search()`) are paginated,
    it is tedious to iterate through all search results. The `paginate` function
    makes it easy to loop through the results in a repeatable manner
    #### Usage

    ```python
    from atlasai.discovery import client

    query = client.paginate(CLIENT_FUNCTION, *args **kwargs)
    ```

    `*args` and `*kwargs` are directly passed to the `CLIENT_FUNCTION`

    Returns a python generator that can be used in a for loop

    ```python
    for obj in query:
        pass
    ```

    #### Example

    ```python
    In [1]: from atlasai.discovery import client

    In [2]: query = client.paginate(
       ...:   client.product.search,
       ...:   odata='''contains(product.internal_name, 'atlasai.')'''
       ...: )

    In [3]: for product in query:
       ...:     print(product.internal_name)
    ```
    """

    offset = kwargs.pop('offset', 0)
    while True:
        response = fn(*args, offset=offset, **kwargs)
        objects = getattr(
            response,
            next(
                k
                for k in dir(response)
                if (
                    not k.startswith('_') and
                    hasattr(getattr(response, k), 'results')
                )
            )
        )
        for result in objects.results:
            yield result

        if not objects.more:
            break

        offset = objects.next_offset

paginator = paginate
