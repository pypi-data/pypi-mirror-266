from copy import deepcopy


def deep_map(data: dict | list, func_cond, func_map, in_place=True):
    if not in_place:
        data = deepcopy(data)

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                deep_map(value, func_cond, func_map, True)
            elif func_cond(value):
                data[key] = func_map(value)
    elif isinstance(data, list):
        for index, value in enumerate(data):
            if isinstance(value, (list, dict)):
                deep_map(value, func_cond, func_map, True)
            elif func_cond(value):
                data[index] = func_map(value)

    return data


def null_to_zero(data: dict | list, in_place=True):
    return deep_map(data, lambda value: value is None, lambda _: 0, in_place)


def deep_round(data: dict | list, ndigits: int, in_place=True):
    return deep_map(data, lambda value: isinstance(value, float), lambda value: round(value, ndigits), in_place)


class EData:
    def __init__(self, data):
        self.data = data

    def null_to_zero(self):
        null_to_zero(self.data)
        return self

    def round(self, ndigits: int):
        deep_round(self.data, ndigits)
        return self

    def map(self, func_cond, func_map):
        deep_map(self.data, func_cond, func_map)
        return self
