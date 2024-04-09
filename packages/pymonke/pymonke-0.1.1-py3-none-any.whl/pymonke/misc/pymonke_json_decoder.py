from json.decoder import JSONDecoder
from uncertainties import ufloat_fromstr

from typing import Any


class PyMonkeJSONDecoder(JSONDecoder):
    def __init__(self) -> None:
        super().__init__(object_hook=self.__object_hook)

    @staticmethod
    def __object_hook(obj: Any) -> Any:
        for key, value in obj.items():
            if isinstance(value, str):
                obj[key] = PyMonkeJSONDecoder.try_to_ufloat(value)
            elif isinstance(value, list):
                obj[key] = [PyMonkeJSONDecoder.try_to_ufloat(x) for x in value]

        return obj

    @staticmethod
    def try_to_ufloat(x: str) -> Any:
        try:
            return ufloat_fromstr(x)
        except ValueError:
            return x