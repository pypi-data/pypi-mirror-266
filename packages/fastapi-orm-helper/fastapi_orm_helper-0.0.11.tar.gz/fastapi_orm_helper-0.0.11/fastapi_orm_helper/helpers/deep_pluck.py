from typing import TypeVar

import pydash

T = TypeVar("T")


def deep_pluck(data: list, deep_key: str):
    keys = deep_key.split('.*.')
    new_data = data
    for key in keys:
        new_data = pydash.flatten(pydash.pluck(new_data, key))
        if new_data is None:
            return []

    return pydash.without(new_data, None)
