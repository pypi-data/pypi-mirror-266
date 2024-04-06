from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ..fable_library.array_ import map as map_3
from ..fable_library.list import (to_array, FSharpList, map as map_1)
from ..fable_library.map import to_list
from ..fable_library.option import (default_arg_with, map as map_2)
from ..fable_library.seq import (to_array as to_array_1, iterate)
from ..fable_library.types import (float32 as float32_1, Array)
from ..fable_library.util import IEnumerable_1
from .types import (Json, IEncoderHelpers_1)

_T1 = TypeVar("_T1")

_T2 = TypeVar("_T2")

_T3 = TypeVar("_T3")

_T4 = TypeVar("_T4")

_T5 = TypeVar("_T5")

_T6 = TypeVar("_T6")

_T7 = TypeVar("_T7")

_T8 = TypeVar("_T8")

_KEY = TypeVar("_KEY")

_VALUE = TypeVar("_VALUE")

_A = TypeVar("_A")

_JSONVALUE = TypeVar("_JSONVALUE")

def float32(value: float32_1) -> Json:
    return Json(2, value)


def list_1(values: FSharpList[Json]) -> Json:
    return Json(6, to_array(values))


def seq(values: IEnumerable_1[Json]) -> Json:
    return Json(6, to_array_1(values))


def dict_1(values: Any) -> Json:
    return Json(5, to_list(values))


def tuple2(enc1: Callable[[_T1], Json], enc2: Callable[[_T2], Json], v1: _T1, v2: _T2) -> Json:
    return Json(6, [enc1(v1), enc2(v2)])


def tuple3(enc1: Callable[[_T1], Json], enc2: Callable[[_T2], Json], enc3: Callable[[_T3], Json], v1: _T1, v2: _T2, v3: _T3) -> Json:
    return Json(6, [enc1(v1), enc2(v2), enc3(v3)])


def tuple4(enc1: Callable[[_T1], Json], enc2: Callable[[_T2], Json], enc3: Callable[[_T3], Json], enc4: Callable[[_T4], Json], v1: _T1, v2: _T2, v3: _T3, v4: _T4) -> Json:
    return Json(6, [enc1(v1), enc2(v2), enc3(v3), enc4(v4)])


def tuple5(enc1: Callable[[_T1], Json], enc2: Callable[[_T2], Json], enc3: Callable[[_T3], Json], enc4: Callable[[_T4], Json], enc5: Callable[[_T5], Json], v1: _T1, v2: _T2, v3: _T3, v4: _T4, v5: _T5) -> Json:
    return Json(6, [enc1(v1), enc2(v2), enc3(v3), enc4(v4), enc5(v5)])


def tuple6(enc1: Callable[[_T1], Json], enc2: Callable[[_T2], Json], enc3: Callable[[_T3], Json], enc4: Callable[[_T4], Json], enc5: Callable[[_T5], Json], enc6: Callable[[_T6], Json], v1: _T1, v2: _T2, v3: _T3, v4: _T4, v5: _T5, v6: _T6) -> Json:
    return Json(6, [enc1(v1), enc2(v2), enc3(v3), enc4(v4), enc5(v5), enc6(v6)])


def tuple7(enc1: Callable[[_T1], Json], enc2: Callable[[_T2], Json], enc3: Callable[[_T3], Json], enc4: Callable[[_T4], Json], enc5: Callable[[_T5], Json], enc6: Callable[[_T6], Json], enc7: Callable[[_T7], Json], v1: _T1, v2: _T2, v3: _T3, v4: _T4, v5: _T5, v6: _T6, v7: _T7) -> Json:
    return Json(6, [enc1(v1), enc2(v2), enc3(v3), enc4(v4), enc5(v5), enc6(v6), enc7(v7)])


def tuple8(enc1: Callable[[_T1], Json], enc2: Callable[[_T2], Json], enc3: Callable[[_T3], Json], enc4: Callable[[_T4], Json], enc5: Callable[[_T5], Json], enc6: Callable[[_T6], Json], enc7: Callable[[_T7], Json], enc8: Callable[[_T8], Json], v1: _T1, v2: _T2, v3: _T3, v4: _T4, v5: _T5, v6: _T6, v7: _T7, v8: _T8) -> Json:
    return Json(6, [enc1(v1), enc2(v2), enc3(v3), enc4(v4), enc5(v5), enc6(v6), enc7(v7), enc8(v8)])


def map(key_encoder: Callable[[_KEY], Json], value_encoder: Callable[[_VALUE], Json], values: Any) -> Json:
    def mapping(tupled_arg: tuple[_KEY, _VALUE], key_encoder: Any=key_encoder, value_encoder: Any=value_encoder, values: Any=values) -> Json:
        return tuple2(key_encoder, value_encoder, tupled_arg[0], tupled_arg[1])

    return list_1(map_1(mapping, to_list(values)))


def Enum_byte(value: Any | None=None) -> Json:
    return Json(7, value)


def Enum_sbyte(value: Any | None=None) -> Json:
    return Json(7, int(value+0x100000000 if value < 0 else value))


def Enum_int16(value: Any | None=None) -> Json:
    return Json(7, int(value+0x100000000 if value < 0 else value))


def Enum_uint16(value: Any | None=None) -> Json:
    return Json(7, value)


def Enum_int(value: Any | None=None) -> Json:
    return Json(7, int(value+0x100000000 if value < 0 else value))


def Enum_uint32(value: Any | None=None) -> Json:
    return Json(7, value)


def option(encoder: Callable[[_A], Json]) -> Callable[[_A | None], Json]:
    def _arrow150(arg: _A | None=None, encoder: Any=encoder) -> Json:
        def def_thunk(__unit: None=None) -> Json:
            return Json(3)

        return default_arg_with(map_2(encoder, arg), def_thunk)

    return _arrow150


def to_json_value(helpers: IEncoderHelpers_1[_JSONVALUE], json: Json) -> _JSONVALUE:
    if json.tag == 7:
        return helpers.encode_integral_number(json.fields[0])

    elif json.tag == 5:
        o: _JSONVALUE = helpers.create_empty_object()
        def action(tupled_arg: tuple[str, Json], helpers: Any=helpers, json: Any=json) -> None:
            helpers.set_property_on_object(o, tupled_arg[0], to_json_value(helpers, tupled_arg[1]))

        iterate(action, json.fields[0])
        return o

    elif json.tag == 1:
        return helpers.encode_char(json.fields[0])

    elif json.tag == 2:
        return helpers.encode_decimal_number(json.fields[0])

    elif json.tag == 3:
        return helpers.encode_null()

    elif json.tag == 4:
        return helpers.encode_bool(json.fields[0])

    elif json.tag == 6:
        def mapping(json_1: Json, helpers: Any=helpers, json: Any=json) -> _JSONVALUE:
            return to_json_value(helpers, json_1)

        arg: Array[_JSONVALUE] = map_3(mapping, json.fields[0], None)
        return helpers.encode_array(arg)

    elif json.tag == 8:
        return helpers.encode_null()

    else: 
        return helpers.encode_string(json.fields[0])



__all__ = ["float32", "list_1", "seq", "dict_1", "tuple2", "tuple3", "tuple4", "tuple5", "tuple6", "tuple7", "tuple8", "map", "Enum_byte", "Enum_sbyte", "Enum_int16", "Enum_uint16", "Enum_int", "Enum_uint32", "option", "to_json_value"]

