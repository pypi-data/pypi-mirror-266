def convert_dataframe_to_dict(obj):
    try:
        import pandas as pd

        if isinstance(obj, pd.DataFrame):
            return obj.to_dict()

        return obj
    except ImportError:
        return obj


def convert_numpy_to_list(obj):
    try:
        import numpy as np

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        return obj
    except ImportError:
        return obj
