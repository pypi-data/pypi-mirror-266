import os


def bool_from_request(params, key, default):
    """Get boolean value from request GET, POST, etc
    :param params: dict POST, GET, etc
    :param key: key to find
    :param default: default value
    :return: boolean
    """
    value = params.get(key, default)

    if isinstance(value, str):
        value = cast_bool_from_str(value)

    return bool(int(value))


def cast_bool_from_str(value):
    if isinstance(value, str):
        if value.lower() in ['true', 'yes', 'on', '1']:
            value = True
        elif value.lower() in ['false', 'no', 'not', 'off', '0']:
            value = False
        else:
            raise ValueError(
                f'Incorrect bool value "{value}". '
                f'It should be one of [1, 0, true, false, yes, no]'
            )
    return value


def get_env(name, default=None, is_bool=False):
    for env_key in ['AIXBLOCK_' + name, 'PLATFORM_' + name, name]:
        value = os.environ.get(env_key)
        if value is not None:
            if is_bool:
                return bool_from_request(os.environ, env_key, default)
            else:
                return value
    return default


def get_bool_env(key, default):
    return get_env(key, default, is_bool=True)
