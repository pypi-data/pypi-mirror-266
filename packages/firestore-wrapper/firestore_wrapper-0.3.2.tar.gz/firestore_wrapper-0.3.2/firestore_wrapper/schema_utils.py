from schema import And, Optional, Schema, SchemaError


def validate_data(data: dict, data_schema: Schema):
    try:
        data_schema.validate(data)
        print("Data is valid.")
    except SchemaError as e:
        print("Data is invalid:", str(e))


def extract_data_type(data_type) -> type:
    if isinstance(data_type, And):
        return data_type.args[0]
    else:
        return data_type


def get_data_type_str(data_type) -> str:
    if data_type is str:
        return 'str'
    elif data_type is int:
        return 'int'
    elif data_type is float:
        return 'float'
    elif data_type is bool:
        return 'bool'
    elif isinstance(data_type, list):
        return f'list[{get_data_type_str(extract_data_type(data_type[0]))}]'
    else:
        raise ValueError(f'Unknown data type: {data_type}')


def data_type_to_input_type(data_type) -> str:
    if data_type is str:
        return 'text'
    elif data_type is int:
        return 'number'
    elif data_type is float:
        return 'number'
    elif data_type is bool:
        return 'checkbox'
    elif isinstance(data_type, list):
        return f'list_{data_type_to_input_type(extract_data_type(data_type[0]))}'
    else:
        raise ValueError(f'Unknown data type: {data_type}')


class KeyInfo:

    def __init__(self, key: str, value):
        self._key = key
        self._value = value

    @property
    def key(self):
        if isinstance(self._key, Optional):
            return self._key.schema
        else:
            return self._key

    @property
    def value(self):
        return self._value

    @property
    def required(self):
        return not isinstance(self._key, Optional)

    @property
    def data_type(self):
        return extract_data_type(self.value)

    @property
    def is_float(self):
        return self.data_type is float

    @property
    def data_type_str(self):
        return get_data_type_str(self.data_type)

    @property
    def input_type(self):
        if self.key == 'email':
            return 'email'
        else:
            return data_type_to_input_type(self.data_type)

    def __str__(self):
        desc = {
            'Key': self.key,
            'Required': self.required,
            'Data Type': self.data_type,
            'Data Type Str': self.data_type_str,
            'Input Type': self.input_type,
        }
        text = ', '.join([f'{k}: {v}' for k, v in desc.items()])
        return f'KeyInfo({text})'


def get_schema_keys(schema: Schema) -> list[KeyInfo]:
    keys_info = []
    for key, value in schema.schema.items():
        keys_info.append(KeyInfo(key, value))
    return keys_info
