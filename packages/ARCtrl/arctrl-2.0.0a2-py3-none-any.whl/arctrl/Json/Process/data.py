from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (choose, singleton, of_array, FSharpList)
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (replace, to_text, printf)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, IOptionalGetter, string, list_1 as list_1_2, IGetters)
from ...fable_modules.thoth_json_core.encode import list_1 as list_1_1
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.comment import Comment
from ...Core.Process.data import Data
from ...Core.Process.data_file import DataFile
from ...Core.uri import URIModule_toString
from ..comment import (Comment_ROCrate_encoder, Comment_ROCrate_decoder, Comment_ISAJson_encoder, Comment_ISAJson_decoder)
from ..context.rocrate.isa_data_context import context_jsonvalue
from ..decode import (Decode_uri, Decode_objectNoAdditionalProperties)
from ..encode import (try_include, try_include_list_opt, default_spaces)
from .data_file import (DataFile_ROCrate_encoder, DataFile_ROCrate_decoder, DataFile_ISAJson_encoder, DataFile_ISAJson_decoder)

def Data_ROCrate_genID(d: Data) -> str:
    match_value: str | None = d.ID
    if match_value is None:
        match_value_1: str | None = d.Name
        if match_value_1 is None:
            return "#EmptyData"

        else: 
            return replace(match_value_1, " ", "_")


    else: 
        return URIModule_toString(match_value)



def Data_ROCrate_encoder(oa: Data) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1274(value_2: str, oa: Any=oa) -> Json:
        return Json(0, value_2)

    def _arrow1275(value_4: DataFile, oa: Any=oa) -> Json:
        return DataFile_ROCrate_encoder(value_4)

    def _arrow1276(comment: Comment, oa: Any=oa) -> Json:
        return Comment_ROCrate_encoder(comment)

    return Json(5, choose(chooser, of_array([("@id", Json(0, Data_ROCrate_genID(oa))), ("@type", list_1_1(singleton(Json(0, "Data")))), try_include("name", _arrow1274, oa.Name), try_include("type", _arrow1275, oa.DataType), try_include_list_opt("comments", _arrow1276, oa.Comments), ("@context", context_jsonvalue)])))


def _arrow1281(get: IGetters) -> Data:
    def _arrow1277(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("@id", Decode_uri)

    def _arrow1278(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("name", string)

    def _arrow1279(__unit: None=None) -> DataFile | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("type", DataFile_ROCrate_decoder)

    def _arrow1280(__unit: None=None) -> FSharpList[Comment] | None:
        arg_7: Decoder_1[FSharpList[Comment]] = list_1_2(Comment_ROCrate_decoder)
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("comments", arg_7)

    return Data(_arrow1277(), _arrow1278(), _arrow1279(), _arrow1280())


Data_ROCrate_decoder: Decoder_1[Data] = object(_arrow1281)

def Data_ISAJson_encoder(oa: Data) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1283(value: str, oa: Any=oa) -> Json:
        return Json(0, value)

    def _arrow1284(value_2: str, oa: Any=oa) -> Json:
        return Json(0, value_2)

    return Json(5, choose(chooser, of_array([try_include("@id", _arrow1283, oa.ID), try_include("name", _arrow1284, oa.Name), try_include("type", DataFile_ISAJson_encoder, oa.DataType), try_include_list_opt("comments", Comment_ISAJson_encoder, oa.Comments)])))


Data_ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "name", "type", "comments", "@type", "@context"])

def _arrow1289(get: IGetters) -> Data:
    def _arrow1285(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("@id", Decode_uri)

    def _arrow1286(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("name", string)

    def _arrow1287(__unit: None=None) -> DataFile | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("type", DataFile_ISAJson_decoder)

    def _arrow1288(__unit: None=None) -> FSharpList[Comment] | None:
        arg_7: Decoder_1[FSharpList[Comment]] = list_1_2(Comment_ISAJson_decoder)
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("comments", arg_7)

    return Data(_arrow1285(), _arrow1286(), _arrow1287(), _arrow1288())


Data_ISAJson_decoder: Decoder_1[Data] = Decode_objectNoAdditionalProperties(Data_ISAJson_allowedFields, _arrow1289)

def ARCtrl_Process_Data__Data_fromISAJsonString_Static_Z721C83C5(s: str) -> Data:
    match_value: FSharpResult_2[Data, str] = Decode_fromString(Data_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Data__Data_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[Data], str]:
    def _arrow1290(f: Data, spaces: Any=spaces) -> str:
        value: Json = Data_ISAJson_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1290


def ARCtrl_Process_Data__Data_fromROCrateJsonString_Static_Z721C83C5(s: str) -> Data:
    match_value: FSharpResult_2[Data, str] = Decode_fromString(Data_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Data__Data_toROCrateJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[Data], str]:
    def _arrow1291(f: Data, spaces: Any=spaces) -> str:
        value: Json = Data_ROCrate_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1291


__all__ = ["Data_ROCrate_genID", "Data_ROCrate_encoder", "Data_ROCrate_decoder", "Data_ISAJson_encoder", "Data_ISAJson_allowedFields", "Data_ISAJson_decoder", "ARCtrl_Process_Data__Data_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_Data__Data_toISAJsonString_Static_71136F3F", "ARCtrl_Process_Data__Data_fromROCrateJsonString_Static_Z721C83C5", "ARCtrl_Process_Data__Data_toROCrateJsonString_Static_71136F3F"]

