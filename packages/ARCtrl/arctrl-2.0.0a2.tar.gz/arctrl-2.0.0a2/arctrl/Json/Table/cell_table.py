from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.array_ import map as map_1
from ...fable_modules.fable_library.map_util import add_to_dict
from ...fable_modules.fable_library.seq import (to_array, map, sort_by)
from ...fable_modules.fable_library.types import Array
from ...fable_modules.fable_library.util import compare_primitives
from ...fable_modules.thoth_json_core.decode import (array as array_1, object, int_1, IGetters)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...Core.Helper.collections_ import Dictionary_tryFind
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Table.composite_cell import CompositeCell
from .composite_cell import (CompositeCell_encoderCompressed, CompositeCell_decoderCompressed)

def array_from_map(otm: Any) -> Array[CompositeCell]:
    def mapping(kv_1: Any, otm: Any=otm) -> CompositeCell:
        return kv_1[0]

    def projection(kv: Any, otm: Any=otm) -> int:
        return kv[1]

    class ObjectExpr1426:
        @property
        def Compare(self) -> Callable[[int, int], int]:
            return compare_primitives

    return to_array(map(mapping, sort_by(projection, otm, ObjectExpr1426())))


def encoder(string_table: Any, oa_table: Any, ot: Array[CompositeCell]) -> Json:
    def mapping(cc: CompositeCell, string_table: Any=string_table, oa_table: Any=oa_table, ot: Any=ot) -> Json:
        return CompositeCell_encoderCompressed(string_table, oa_table, cc)

    return Json(6, map_1(mapping, ot, None))


def decoder(string_table: Array[str], oa_table: Array[OntologyAnnotation]) -> Decoder_1[Array[CompositeCell]]:
    return array_1(CompositeCell_decoderCompressed(string_table, oa_table))


def encode_cell(otm: Any, cc: CompositeCell) -> Json:
    match_value: int | None = Dictionary_tryFind(cc, otm)
    if match_value is None:
        i_1: int = len(otm) or 0
        add_to_dict(otm, cc, i_1)
        return Json(7, int(i_1+0x100000000 if i_1 < 0 else i_1))

    else: 
        i: int = match_value or 0
        return Json(7, int(i+0x100000000 if i < 0 else i))



def decode_cell(ot: Array[CompositeCell]) -> Decoder_1[CompositeCell]:
    def _arrow1427(get: IGetters, ot: Any=ot) -> CompositeCell:
        i: int = get.Required.Raw(int_1) or 0
        return ot[i]

    return object(_arrow1427)


__all__ = ["array_from_map", "encoder", "decoder", "encode_cell", "decode_cell"]

