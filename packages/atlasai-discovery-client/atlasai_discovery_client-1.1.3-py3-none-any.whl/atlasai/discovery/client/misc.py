def build_input_builder(helpers=None):
    helpers = helpers or {}

    def wrapper(Input, **kwargs):
        params = {}
        for field in Input:
            k = field.name
            if k not in kwargs:
                continue

            v = kwargs[k]
            params[k] = helpers[k](v) if k in helpers else v

        return Input(**params)

    return wrapper

def build_namespace_input(input_, class_name=None):
    assert hasattr(input_, '__field_names__')

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, name, value):
        if name not in self.__field_names__:
            raise ValueError(f'Unsupported attribute: {name}')
        self.__dict__[name] = value

    attributes = {
        '__field_names__': input_.__field_names__,
        '__init__': __init__,
        '__setattr__': __setattr__,
    }

    return type(
        class_name or 'NamespacedInput',
        (),
        attributes
    )

def input_as_dict(input_):
    if isinstance(input_, dict):
        return input_
    elif hasattr(input_, '__dict__'):
        return input_.__dict__
    else:
        raise ValueError(f'Unsupported input: {input_}')
