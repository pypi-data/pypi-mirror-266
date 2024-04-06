from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ..fable_modules.fable_library.array_ import map as map_1
from ..fable_modules.fable_library.date import to_string
from ..fable_modules.fable_library.list import (is_empty as is_empty_1, map as map_2, FSharpList)
from ..fable_modules.fable_library.option import (value as value_2, default_arg)
from ..fable_modules.fable_library.seq import (is_empty, map)
from ..fable_modules.fable_library.types import Array
from ..fable_modules.thoth_json_core.encode import (seq, list_1 as list_1_1)
from ..fable_modules.thoth_json_core.types import Json

_VALUE = TypeVar("_VALUE")

__A = TypeVar("__A")

def try_include(name: str, encoder: Callable[[_VALUE], Json], value: _VALUE | None=None) -> tuple[str, Json]:
    return (name, encoder(value_2(value)) if (value is not None) else Json(3))


def try_include_seq(name: __A, encoder: Callable[[_VALUE], Json], value: Any) -> tuple[__A, Json]:
    return (name, Json(3) if is_empty(value) else seq(map(encoder, value)))


def try_include_array(name: __A, encoder: Callable[[_VALUE], Json], value: Array[_VALUE]) -> tuple[__A, Json]:
    return (name, Json(3) if (len(value) == 0) else Json(6, map_1(encoder, value, None)))


def try_include_list(name: __A, encoder: Callable[[_VALUE], Json], value: FSharpList[_VALUE]) -> tuple[__A, Json]:
    return (name, Json(3) if is_empty_1(value) else list_1_1(map_2(encoder, value)))


def try_include_list_opt(name: __A, encoder: Callable[[_VALUE], Json], value: FSharpList[_VALUE] | None=None) -> tuple[__A, Json]:
    def _arrow946(__unit: None=None, name: Any=name, encoder: Any=encoder, value: Any=value) -> Json:
        o: FSharpList[_VALUE] = value
        return Json(3) if is_empty_1(o) else list_1_1(map_2(encoder, o))

    return (name, _arrow946() if (value is not None) else Json(3))


DefaultSpaces: int = 0

def default_spaces(spaces: int | None=None) -> int:
    return default_arg(spaces, DefaultSpaces)


def date_time(d: Any) -> Json:
    return Json(0, to_string(d, "O", {}).split("+")[0])


__all__ = ["try_include", "try_include_seq", "try_include_array", "try_include_list", "try_include_list_opt", "DefaultSpaces", "default_spaces", "date_time"]

