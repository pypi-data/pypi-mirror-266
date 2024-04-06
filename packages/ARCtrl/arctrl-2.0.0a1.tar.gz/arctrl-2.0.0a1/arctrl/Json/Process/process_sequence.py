from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (FSharpList, map)
from ...fable_modules.fable_library.reflection import (TypeInfo, class_type)
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.thoth_json_core.decode import list_1 as list_1_1
from ...fable_modules.thoth_json_core.encode import list_1 as list_1_2
from ...fable_modules.thoth_json_core.types import Json
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.Process.process import Process
from ..encode import default_spaces
from .process import (Process_ISAJson_decoder, Process_ISAJson_encoder, Process_ROCrate_decoder, Process_ROCrate_encoder)

def _expr1360() -> TypeInfo:
    return class_type("ARCtrl.Json.ProcessSequence", None, ProcessSequence)


class ProcessSequence:
    ...

ProcessSequence_reflection = _expr1360

def ProcessSequence_fromISAJsonString_Z721C83C5(s: str) -> FSharpList[Process]:
    match_value: FSharpResult_2[FSharpList[Process], str] = Decode_fromString(list_1_1(Process_ISAJson_decoder), s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ProcessSequence_toISAJsonString_71136F3F(spaces: int | None=None) -> Callable[[FSharpList[Process]], str]:
    def _arrow1361(f: FSharpList[Process], spaces: Any=spaces) -> str:
        value: Json = list_1_2(map(Process_ISAJson_encoder, f))
        return to_string(default_spaces(spaces), value)

    return _arrow1361


def ProcessSequence_fromROCrateJsonString_Z721C83C5(s: str) -> FSharpList[Process]:
    match_value: FSharpResult_2[FSharpList[Process], str] = Decode_fromString(list_1_1(Process_ROCrate_decoder), s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ProcessSequence_toROCrateJsonString_39E0BC3F(study_name: str | None=None, assay_name: str | None=None, spaces: int | None=None) -> Callable[[FSharpList[Process]], str]:
    def _arrow1362(f: FSharpList[Process], study_name: Any=study_name, assay_name: Any=assay_name, spaces: Any=spaces) -> str:
        def mapping(oa: Process) -> Json:
            return Process_ROCrate_encoder(study_name, assay_name, oa)

        value: Json = list_1_2(map(mapping, f))
        return to_string(default_spaces(spaces), value)

    return _arrow1362


__all__ = ["ProcessSequence_reflection", "ProcessSequence_fromISAJsonString_Z721C83C5", "ProcessSequence_toISAJsonString_71136F3F", "ProcessSequence_fromROCrateJsonString_Z721C83C5", "ProcessSequence_toROCrateJsonString_39E0BC3F"]

