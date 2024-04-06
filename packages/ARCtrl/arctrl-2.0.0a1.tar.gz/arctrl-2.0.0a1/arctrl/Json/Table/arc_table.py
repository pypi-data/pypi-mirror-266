from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ...fable_modules.fable_library.array_ import (iterate_indexed, fold, fill)
from ...fable_modules.fable_library.list import (FSharpList, empty as empty_1)
from ...fable_modules.fable_library.map import (of_seq, empty as empty_2)
from ...fable_modules.fable_library.map_util import (get_item_from_dict, add_to_dict)
from ...fable_modules.fable_library.mutable_map import Dictionary
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.range import range_big_int
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.seq import (to_list, delay, append, singleton, map, empty, collect, to_array)
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.fable_library.types import Array
from ...fable_modules.fable_library.util import (IEnumerable_1, compare_arrays, equal_arrays, array_hash, equals, to_enumerable, int32_to_string, ignore, safe_hash)
from ...fable_modules.thoth_json_core.decode import (object, list_1 as list_1_1, IOptionalGetter, map_0027, tuple2 as tuple2_1, int_1, IRequiredGetter, string, IGetters, array as array_1, Helpers_prependPath)
from ...fable_modules.thoth_json_core.encode import (list_1, map as map_1, tuple2)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1, ErrorReason_1, IDecoderHelpers_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Table.arc_table import ArcTable
from ...Core.Table.composite_cell import CompositeCell
from ...Core.Table.composite_header import CompositeHeader
from ..encode import default_spaces
from ..string_table import (encode_string, decode_string, decoder as decoder_2, encoder as encoder_2, array_from_map as array_from_map_2)
from .cell_table import (encode_cell, decode_cell, decoder as decoder_4, encoder, array_from_map)
from .composite_cell import (CompositeCell_encoder, CompositeCell_decoder)
from .composite_header import (CompositeHeader_encoder, CompositeHeader_decoder)
from .oatable import (decoder as decoder_3, encoder as encoder_1, array_from_map as array_from_map_1)

__A_ = TypeVar("__A_")

_VALUE_ = TypeVar("_VALUE_")

_VALUE = TypeVar("_VALUE")

def ArcTable_encoder(table: ArcTable) -> Json:
    def _arrow1443(__unit: None=None, table: Any=table) -> IEnumerable_1[tuple[str, Json]]:
        def _arrow1442(__unit: None=None) -> IEnumerable_1[tuple[str, Json]]:
            def _arrow1435(__unit: None=None) -> IEnumerable_1[Json]:
                return map(CompositeHeader_encoder, table.Headers)

            def _arrow1441(__unit: None=None) -> IEnumerable_1[tuple[str, Json]]:
                def key_encoder(tupled_arg: tuple[int, int]) -> Json:
                    def _arrow1436(value: int, tupled_arg: Any=tupled_arg) -> Json:
                        return Json(7, int(value+0x100000000 if value < 0 else value))

                    def _arrow1437(value_2: int, tupled_arg: Any=tupled_arg) -> Json:
                        return Json(7, int(value_2+0x100000000 if value_2 < 0 else value_2))

                    return tuple2(_arrow1436, _arrow1437, tupled_arg[0], tupled_arg[1])

                def _arrow1439(__unit: None=None) -> IEnumerable_1[tuple[tuple[int, int], CompositeCell]]:
                    def _arrow1438(match_value: Any) -> IEnumerable_1[tuple[tuple[int, int], CompositeCell]]:
                        active_pattern_result: tuple[tuple[int, int], CompositeCell] = match_value
                        return singleton((active_pattern_result[0], active_pattern_result[1]))

                    return collect(_arrow1438, table.Values)

                class ObjectExpr1440:
                    @property
                    def Compare(self) -> Callable[[tuple[int, int], tuple[int, int]], int]:
                        return compare_arrays

                return singleton(("values", map_1(key_encoder, CompositeCell_encoder, of_seq(to_list(delay(_arrow1439)), ObjectExpr1440())))) if (len(table.Values) != 0) else empty()

            return append(singleton(("header", list_1(to_list(delay(_arrow1435))))) if (len(table.Headers) != 0) else empty(), delay(_arrow1441))

        return append(singleton(("name", Json(0, table.Name))), delay(_arrow1442))

    return Json(5, to_list(delay(_arrow1443)))


def _arrow1449(get: IGetters) -> ArcTable:
    def _arrow1444(__unit: None=None) -> FSharpList[CompositeHeader] | None:
        arg_1: Decoder_1[FSharpList[CompositeHeader]] = list_1_1(CompositeHeader_decoder)
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("header", arg_1)

    decoded_header: Array[CompositeHeader] = list(default_arg(_arrow1444(), empty_1()))
    def _arrow1445(__unit: None=None) -> Any | None:
        arg_3: Decoder_1[Any] = map_0027(tuple2_1(int_1, int_1), CompositeCell_decoder)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("values", arg_3)

    class ObjectExpr1446:
        @property
        def Compare(self) -> Callable[[tuple[int, int], tuple[int, int]], int]:
            return compare_arrays

    class ObjectExpr1447:
        @property
        def Equals(self) -> Callable[[tuple[int, int], tuple[int, int]], bool]:
            return equal_arrays

        @property
        def GetHashCode(self) -> Callable[[tuple[int, int]], int]:
            return array_hash

    decoded_values: Any = Dictionary(default_arg(_arrow1445(), empty_2(ObjectExpr1446())), ObjectExpr1447())
    def _arrow1448(__unit: None=None) -> str:
        object_arg_2: IRequiredGetter = get.Required
        return object_arg_2.Field("name", string)

    return ArcTable.create(_arrow1448(), decoded_header, decoded_values)


ArcTable_decoder: Decoder_1[ArcTable] = object(_arrow1449)

def ArcTable_encoderCompressedColumn(column_index: int, row_count: int, cell_table: Any, table: ArcTable) -> Json:
    if True if table.Headers[column_index].IsIOType else (row_count < 100):
        def _arrow1451(__unit: None=None, column_index: Any=column_index, row_count: Any=row_count, cell_table: Any=cell_table, table: Any=table) -> IEnumerable_1[Json]:
            def _arrow1450(r: int) -> Json:
                return encode_cell(cell_table, get_item_from_dict(table.Values, (column_index, r)))

            return map(_arrow1450, range_big_int(0, 1, row_count - 1))

        return Json(6, to_array(delay(_arrow1451)))

    else: 
        current: CompositeCell = get_item_from_dict(table.Values, (column_index, 0))
        from_: int = 0
        def _arrow1459(__unit: None=None, column_index: Any=column_index, row_count: Any=row_count, cell_table: Any=cell_table, table: Any=table) -> IEnumerable_1[Json]:
            def _arrow1455(i: int) -> IEnumerable_1[Json]:
                next_1: CompositeCell = get_item_from_dict(table.Values, (column_index, i))
                def _arrow1452(__unit: None=None) -> Json:
                    value: int = from_ or 0
                    return Json(7, int(value+0x100000000 if value < 0 else value))

                def _arrow1453(__unit: None=None) -> Json:
                    value_1: int = (i - 1) or 0
                    return Json(7, int(value_1+0x100000000 if value_1 < 0 else value_1))

                def _arrow1454(__unit: None=None) -> IEnumerable_1[Json]:
                    nonlocal current, from_
                    current = next_1
                    from_ = i or 0
                    return empty()

                return append(singleton(Json(5, to_enumerable([("f", _arrow1452()), ("t", _arrow1453()), ("v", encode_cell(cell_table, current))]))), delay(_arrow1454)) if (not equals(next_1, current)) else empty()

            def _arrow1458(__unit: None=None) -> IEnumerable_1[Json]:
                def _arrow1456(__unit: None=None) -> Json:
                    value_2: int = from_ or 0
                    return Json(7, int(value_2+0x100000000 if value_2 < 0 else value_2))

                def _arrow1457(__unit: None=None) -> Json:
                    value_3: int = (row_count - 1) or 0
                    return Json(7, int(value_3+0x100000000 if value_3 < 0 else value_3))

                return singleton(Json(5, to_enumerable([("f", _arrow1456()), ("t", _arrow1457()), ("v", encode_cell(cell_table, current))])))

            return append(collect(_arrow1455, range_big_int(1, 1, row_count - 1)), delay(_arrow1458))

        return Json(6, to_array(delay(_arrow1459)))



def ArcTable_decoderCompressedColumn(cell_table: Array[CompositeCell], table: ArcTable, column_index: int) -> Decoder_1[None]:
    class ObjectExpr1461(Decoder_1[None]):
        def Decode(self, helper: IDecoderHelpers_1[__A_], column: __A_, cell_table: Any=cell_table, table: Any=table, column_index: Any=column_index) -> FSharpResult_2[None, tuple[str, ErrorReason_1[__A_]]]:
            match_value: FSharpResult_2[Array[CompositeCell], tuple[str, ErrorReason_1[__A_]]] = array_1(decode_cell(cell_table)).Decode(helper, column)
            if match_value.tag == 1:
                def _arrow1460(get: IGetters) -> None:
                    from_: int
                    object_arg: IRequiredGetter = get.Required
                    from_ = object_arg.Field("f", int_1)
                    to_: int
                    object_arg_1: IRequiredGetter = get.Required
                    to_ = object_arg_1.Field("t", int_1)
                    value: CompositeCell
                    arg_5: Decoder_1[CompositeCell] = decode_cell(cell_table)
                    object_arg_2: IRequiredGetter = get.Required
                    value = object_arg_2.Field("v", arg_5)
                    for i in range(from_, to_ + 1, 1):
                        add_to_dict(table.Values, (column_index, i), value)

                range_decoder: Decoder_1[None] = object(_arrow1460)
                match_value_1: FSharpResult_2[Array[None], tuple[str, ErrorReason_1[__A_]]] = array_1(range_decoder).Decode(helper, column)
                return FSharpResult_2(1, match_value_1.fields[0]) if (match_value_1.tag == 1) else FSharpResult_2(0, None)

            else: 
                def action(r: int, cell: CompositeCell) -> None:
                    add_to_dict(table.Values, (column_index, r), cell)

                iterate_indexed(action, match_value.fields[0])
                return FSharpResult_2(0, None)


    return ObjectExpr1461()


def ArcTable_arrayi(decoderi: Callable[[int], Decoder_1[_VALUE]]) -> Decoder_1[Array[_VALUE]]:
    class ObjectExpr1463(Decoder_1[Array[_VALUE_]]):
        def Decode(self, helpers: IDecoderHelpers_1[__A_], value: __A_, decoderi: Any=decoderi) -> FSharpResult_2[Array[_VALUE_], tuple[str, ErrorReason_1[__A_]]]:
            if helpers.is_array(value):
                i: int = -1
                tokens: Array[__A_] = helpers.as_array(value)
                def folder(acc: FSharpResult_2[Array[_VALUE_], tuple[str, ErrorReason_1[__A_]]], value_1: __A_) -> FSharpResult_2[Array[_VALUE_], tuple[str, ErrorReason_1[__A_]]]:
                    nonlocal i
                    i = (i + 1) or 0
                    if acc.tag == 0:
                        acc_1: Array[_VALUE_] = acc.fields[0]
                        match_value: FSharpResult_2[_VALUE_, tuple[str, ErrorReason_1[__A_]]] = decoderi(i).Decode(helpers, value_1)
                        if match_value.tag == 0:
                            acc_1[i] = match_value.fields[0]
                            return FSharpResult_2(0, acc_1)

                        else: 
                            def _arrow1462(__unit: None=None, acc: Any=acc, value_1: Any=value_1) -> tuple[str, ErrorReason_1[__A_]]:
                                tupled_arg: tuple[str, ErrorReason_1[__A_]] = match_value.fields[0]
                                return Helpers_prependPath((".[" + int32_to_string(i)) + "]", tupled_arg[0], tupled_arg[1])

                            return FSharpResult_2(1, _arrow1462())


                    else: 
                        return acc


                return fold(folder, FSharpResult_2(0, fill([0] * len(tokens), 0, len(tokens), None)), tokens)

            else: 
                return FSharpResult_2(1, ("", ErrorReason_1(0, "an array", value)))


    return ObjectExpr1463()


def ArcTable_encoderCompressed(string_table: Any, oa_table: Any, cell_table: Any, table: ArcTable) -> Json:
    def _arrow1469(__unit: None=None, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, table: Any=table) -> IEnumerable_1[tuple[str, Json]]:
        def _arrow1468(__unit: None=None) -> IEnumerable_1[tuple[str, Json]]:
            def _arrow1464(__unit: None=None) -> IEnumerable_1[Json]:
                return map(CompositeHeader_encoder, table.Headers)

            def _arrow1467(__unit: None=None) -> IEnumerable_1[tuple[str, Json]]:
                if len(table.Values) != 0:
                    row_count: int = table.RowCount or 0
                    def _arrow1466(__unit: None=None) -> IEnumerable_1[Json]:
                        def _arrow1465(c: int) -> Json:
                            return ArcTable_encoderCompressedColumn(c, row_count, cell_table, table)

                        return map(_arrow1465, range_big_int(0, 1, table.ColumnCount - 1))

                    return singleton(("c", Json(6, to_array(delay(_arrow1466)))))

                else: 
                    return empty()


            return append(singleton(("h", list_1(to_list(delay(_arrow1464))))) if (len(table.Headers) != 0) else empty(), delay(_arrow1467))

        return append(singleton(("n", encode_string(string_table, table.Name))), delay(_arrow1468))

    return Json(5, to_list(delay(_arrow1469)))


def ArcTable_decoderCompressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[ArcTable]:
    def _arrow1475(get: IGetters, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table) -> ArcTable:
        def _arrow1470(__unit: None=None) -> FSharpList[CompositeHeader] | None:
            arg_1: Decoder_1[FSharpList[CompositeHeader]] = list_1_1(CompositeHeader_decoder)
            object_arg: IOptionalGetter = get.Optional
            return object_arg.Field("h", arg_1)

        decoded_header: Array[CompositeHeader] = list(default_arg(_arrow1470(), empty_1()))
        def _arrow1471(__unit: None=None) -> str:
            arg_3: Decoder_1[str] = decode_string(string_table)
            object_arg_1: IRequiredGetter = get.Required
            return object_arg_1.Field("n", arg_3)

        class ObjectExpr1472:
            @property
            def Equals(self) -> Callable[[tuple[int, int], tuple[int, int]], bool]:
                return equal_arrays

            @property
            def GetHashCode(self) -> Callable[[tuple[int, int]], int]:
                return array_hash

        table: ArcTable = ArcTable.create(_arrow1471(), decoded_header, Dictionary([], ObjectExpr1472()))
        def _arrow1474(__unit: None=None) -> Array[None] | None:
            def _arrow1473(column_index: int) -> Decoder_1[None]:
                return ArcTable_decoderCompressedColumn(cell_table, table, column_index)

            arg_5: Decoder_1[Array[None]] = ArcTable_arrayi(_arrow1473)
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("c", arg_5)

        ignore(_arrow1474())
        return table

    return object(_arrow1475)


def ARCtrl_ArcTable__ArcTable_fromJsonString_Static_Z721C83C5(s: str) -> ArcTable:
    match_value: FSharpResult_2[ArcTable, str] = Decode_fromString(ArcTable_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_ArcTable__ArcTable_toJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ArcTable], str]:
    def _arrow1476(obj: ArcTable, spaces: Any=spaces) -> str:
        value: Json = ArcTable_encoder(obj)
        return to_string(default_spaces(spaces), value)

    return _arrow1476


def ARCtrl_ArcTable__ArcTable_ToJsonString_71136F3F(this: ArcTable, spaces: int | None=None) -> str:
    return ARCtrl_ArcTable__ArcTable_toJsonString_Static_71136F3F(spaces)(this)


def ARCtrl_ArcTable__ArcTable_fromCompressedJsonString_Static_Z721C83C5(json_string: str) -> ArcTable:
    def _arrow1478(get: IGetters, json_string: Any=json_string) -> ArcTable:
        string_table: Array[str]
        object_arg: IRequiredGetter = get.Required
        string_table = object_arg.Field("stringTable", decoder_2)
        oa_table: Array[OntologyAnnotation]
        arg_3: Decoder_1[Array[OntologyAnnotation]] = decoder_3(string_table)
        object_arg_1: IRequiredGetter = get.Required
        oa_table = object_arg_1.Field("oaTable", arg_3)
        def _arrow1477(__unit: None=None) -> Array[CompositeCell]:
            arg_5: Decoder_1[Array[CompositeCell]] = decoder_4(string_table, oa_table)
            object_arg_2: IRequiredGetter = get.Required
            return object_arg_2.Field("cellTable", arg_5)

        arg_7: Decoder_1[ArcTable] = ArcTable_decoderCompressed(string_table, oa_table, _arrow1477())
        object_arg_3: IRequiredGetter = get.Required
        return object_arg_3.Field("table", arg_7)

    match_value: FSharpResult_2[ArcTable, str] = Decode_fromString(object(_arrow1478), json_string)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_ArcTable__ArcTable_ToCompressedJsonString_71136F3F(this: ArcTable, spaces: int | None=None) -> str:
    spaces_1: int = default_spaces(spaces) or 0
    string_table: Any = dict([])
    class ObjectExpr1479:
        @property
        def Equals(self) -> Callable[[OntologyAnnotation, OntologyAnnotation], bool]:
            return equals

        @property
        def GetHashCode(self) -> Callable[[OntologyAnnotation], int]:
            return safe_hash

    oa_table: Any = Dictionary([], ObjectExpr1479())
    class ObjectExpr1480:
        @property
        def Equals(self) -> Callable[[CompositeCell, CompositeCell], bool]:
            return equals

        @property
        def GetHashCode(self) -> Callable[[CompositeCell], int]:
            return safe_hash

    cell_table: Any = Dictionary([], ObjectExpr1480())
    arc_table: Json = ArcTable_encoderCompressed(string_table, oa_table, cell_table, this)
    return to_string(spaces_1, Json(5, to_enumerable([("cellTable", encoder(string_table, oa_table, array_from_map(cell_table))), ("oaTable", encoder_1(string_table, array_from_map_1(oa_table))), ("stringTable", encoder_2(array_from_map_2(string_table))), ("table", arc_table)])))


def ARCtrl_ArcTable__ArcTable_toCompressedJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ArcTable], str]:
    def _arrow1481(obj: ArcTable, spaces: Any=spaces) -> str:
        return ARCtrl_ArcTable__ArcTable_ToCompressedJsonString_71136F3F(obj, spaces)

    return _arrow1481


__all__ = ["ArcTable_encoder", "ArcTable_decoder", "ArcTable_encoderCompressedColumn", "ArcTable_decoderCompressedColumn", "ArcTable_arrayi", "ArcTable_encoderCompressed", "ArcTable_decoderCompressed", "ARCtrl_ArcTable__ArcTable_fromJsonString_Static_Z721C83C5", "ARCtrl_ArcTable__ArcTable_toJsonString_Static_71136F3F", "ARCtrl_ArcTable__ArcTable_ToJsonString_71136F3F", "ARCtrl_ArcTable__ArcTable_fromCompressedJsonString_Static_Z721C83C5", "ARCtrl_ArcTable__ArcTable_ToCompressedJsonString_71136F3F", "ARCtrl_ArcTable__ArcTable_toCompressedJsonString_Static_71136F3F"]

