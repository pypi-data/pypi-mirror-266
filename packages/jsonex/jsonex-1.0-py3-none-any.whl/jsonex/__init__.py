import json


class JsonEx:

    @staticmethod
    def dump(
            data,
            skipkeys=False,
            ensure_ascii=True,
            check_circular=True,
            allow_nan=True,
            cls=None,
            indent=None,
            separators=None,
            default=None,
            sort_keys=False
    ):
        data = JsonEx._fix_data(data)
        
        return json.dumps(data, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, allow_nan=allow_nan, cls=cls, indent=indent, separators=separators, default=default, sort_keys=sort_keys)

    @staticmethod
    def _fix_data(data):
        for key, value in JsonEx.data_iteration(data):
            if JsonEx._is_custom_type(value):
                data[key] = f"[custom type: {type(value).__name__}]"
            elif isinstance(value, dict):
                data[key] = JsonEx._fix_data(value)
            elif isinstance(value, list):
                data[key] = JsonEx._fix_data(value)
            elif isinstance(value, set):
                data[key] = list(value)

        return data

    @staticmethod
    def _is_custom_type(obj):
        default_types = (int, float, str, list, dict, tuple, set, bool, type(None))
        return not isinstance(obj, default_types)

    @staticmethod
    def data_iteration(data):
        if isinstance(data, dict):
            for key, value in data.items():
                yield key, value
        elif isinstance(data, (list, set)):
            for key, value in enumerate(data if isinstance(data, list) else list(data)):
                yield key, value
