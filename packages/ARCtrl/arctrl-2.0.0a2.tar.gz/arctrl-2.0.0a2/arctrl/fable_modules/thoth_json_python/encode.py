from __future__ import annotations
import json as json_1
from typing import Any
from ..fable_library.list import FSharpList
from ..fable_library.types import (Array, uint32)
from ..fable_library.util import IEnumerable_1
from ..thoth_json_core.encode import to_json_value
from ..thoth_json_core.types import (IEncoderHelpers_1, Json)

class ObjectExpr151(IEncoderHelpers_1[Any]):
    def encode_string(self, value: str) -> Any:
        return value

    def encode_char(self, value_1: str) -> Any:
        return value_1

    def encode_decimal_number(self, value_2: float) -> Any:
        return value_2

    def encode_bool(self, value_3: bool) -> Any:
        return value_3

    def encode_null(self, __unit: None=None) -> Any:
        return None

    def create_empty_object(self, __unit: None=None) -> Any:
        return {}

    def set_property_on_object(self, o: Any, key: str, value_4: Any=None) -> None:
        o[key] = value_4

    def encode_array(self, values: Array[Any]) -> Any:
        return values

    def encode_list(self, values_1: FSharpList[Any]) -> Any:
        return Array.from_(values_1)

    def encode_seq(self, values_2: IEnumerable_1[Any]) -> Any:
        return Array.from_(values_2)

    def encode_integral_number(self, value_5: uint32) -> Any:
        return value_5


helpers: IEncoderHelpers_1[Any] = ObjectExpr151()

def to_string(space: int, value: Json) -> str:
    json: Any = to_json_value(helpers, value)
    if space == 0:
        return json_1.dumps(json, separators = [",", ":"], ensure_ascii = False)

    else: 
        return json_1.dumps(json, indent = space)



__all__ = ["helpers", "to_string"]

