def get_tag_value(tags, keys):
    values = {
        tag.name: tag.value
        for tag in tags
        if tag.name in keys
    }

    return next(
        iter([
            values[k]
            for k in keys
            if k in values
        ]),
        None,
    )

def contains_tag(tags, keys, values=None):
    _values = [
        tag.value
        for tag in tags
        if tag.name in keys
    ]

    if not values and len(_values):
        return True

    if set(_values).intersection(values):
        return True

    return False
