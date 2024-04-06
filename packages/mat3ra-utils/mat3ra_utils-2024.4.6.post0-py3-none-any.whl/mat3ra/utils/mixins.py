import numpy as np


class RoundNumericValuesMixin(object):
    # Default rounding precision in decimal places
    __round_precision__ = 9

    @classmethod
    def round_array_or_number(cls, array, decimal_places=__round_precision__):
        return np.round(array, cls.__round_precision__).tolist()
