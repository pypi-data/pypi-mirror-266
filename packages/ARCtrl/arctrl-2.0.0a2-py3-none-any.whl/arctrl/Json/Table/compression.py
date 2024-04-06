from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ...fable_modules.fable_library.mutable_map import Dictionary
from ...fable_modules.fable_library.types import Array
from ...fable_modules.fable_library.util import (equals, safe_hash, to_enumerable)
from ...fable_modules.thoth_json_core.decode import (object, IRequiredGetter, IGetters)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Table.composite_cell import CompositeCell
from ..string_table import (encoder as encoder_3, array_from_map as array_from_map_2, decoder as decoder_1)
from .cell_table import (encoder as encoder_1, array_from_map, decoder as decoder_3)
from .oatable import (encoder as encoder_2, array_from_map as array_from_map_1, decoder as decoder_2)

_A = TypeVar("_A")

__A = TypeVar("__A")

__B = TypeVar("__B")

def encode(encoder: Callable[[Any, Any, Any, _A], Json], obj: _A) -> Json:
    string_table: Any = dict([])
    class ObjectExpr1431:
        @property
        def Equals(self) -> Callable[[OntologyAnnotation, OntologyAnnotation], bool]:
            return equals

        @property
        def GetHashCode(self) -> Callable[[OntologyAnnotation], int]:
            return safe_hash

    oa_table: Any = Dictionary([], ObjectExpr1431())
    class ObjectExpr1432:
        @property
        def Equals(self) -> Callable[[CompositeCell, CompositeCell], bool]:
            return equals

        @property
        def GetHashCode(self) -> Callable[[CompositeCell], int]:
            return safe_hash

    cell_table: Any = Dictionary([], ObjectExpr1432())
    arc_study: Json = encoder(string_table, oa_table, cell_table, obj)
    return Json(5, to_enumerable([("cellTable", encoder_1(string_table, oa_table, array_from_map(cell_table))), ("oaTable", encoder_2(string_table, array_from_map_1(oa_table))), ("stringTable", encoder_3(array_from_map_2(string_table))), ("object", arc_study)]))


def decode(decoder: Callable[[Array[str], Array[OntologyAnnotation], Array[CompositeCell]], __A]) -> Decoder_1[Any]:
    def _arrow1434(get: IGetters, decoder: Any=decoder) -> __B:
        string_table: Array[str]
        object_arg: IRequiredGetter = get.Required
        string_table = object_arg.Field("stringTable", decoder_1)
        oa_table: Array[OntologyAnnotation]
        arg_3: Decoder_1[Array[OntologyAnnotation]] = decoder_2(string_table)
        object_arg_1: IRequiredGetter = get.Required
        oa_table = object_arg_1.Field("oaTable", arg_3)
        def _arrow1433(__unit: None=None) -> Array[CompositeCell]:
            arg_5: Decoder_1[Array[CompositeCell]] = decoder_3(string_table, oa_table)
            object_arg_2: IRequiredGetter = get.Required
            return object_arg_2.Field("cellTable", arg_5)

        arg_7: __A = decoder(string_table, oa_table, _arrow1433())
        object_arg_3: IRequiredGetter = get.Required
        return object_arg_3.Field("object", arg_7)

    return object(_arrow1434)


__all__ = ["encode", "decode"]

