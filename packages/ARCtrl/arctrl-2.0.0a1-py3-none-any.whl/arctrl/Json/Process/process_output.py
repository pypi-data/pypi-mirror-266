from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import of_array
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.thoth_json_core.decode import (one_of, map)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.Process.data import Data
from ...Core.Process.material import Material
from ...Core.Process.process_output import ProcessOutput
from ...Core.Process.sample import Sample
from ..encode import default_spaces
from .data import (Data_ROCrate_encoder, Data_ROCrate_decoder, Data_ISAJson_encoder, Data_ISAJson_decoder)
from .material import (Material_ROCrate_encoder, Material_ROCrate_decoder, Material_ISAJson_encoder, Material_ISAJson_decoder)
from .sample import (Sample_ROCrate_encoder, Sample_ROCrate_decoder, Sample_ISAJson_encoder, Sample_ISAJson_decoder)

def ProcessOutput_ROCrate_encoder(value: ProcessOutput) -> Json:
    if value.tag == 1:
        return Data_ROCrate_encoder(value.fields[0])

    elif value.tag == 2:
        return Material_ROCrate_encoder(value.fields[0])

    else: 
        return Sample_ROCrate_encoder(value.fields[0])



def _arrow1351(Item: Sample) -> ProcessOutput:
    return ProcessOutput(0, Item)


def _arrow1352(Item_1: Data) -> ProcessOutput:
    return ProcessOutput(1, Item_1)


def _arrow1353(Item_2: Material) -> ProcessOutput:
    return ProcessOutput(2, Item_2)


ProcessOutput_ROCrate_decoder: Decoder_1[ProcessOutput] = one_of(of_array([map(_arrow1351, Sample_ROCrate_decoder), map(_arrow1352, Data_ROCrate_decoder), map(_arrow1353, Material_ROCrate_decoder)]))

def ProcessOutput_ISAJson_encoder(value: ProcessOutput) -> Json:
    if value.tag == 1:
        return Data_ISAJson_encoder(value.fields[0])

    elif value.tag == 2:
        return Material_ISAJson_encoder(value.fields[0])

    else: 
        return Sample_ISAJson_encoder(value.fields[0])



def _arrow1355(Item: Sample) -> ProcessOutput:
    return ProcessOutput(0, Item)


def _arrow1356(Item_1: Data) -> ProcessOutput:
    return ProcessOutput(1, Item_1)


def _arrow1357(Item_2: Material) -> ProcessOutput:
    return ProcessOutput(2, Item_2)


ProcessOutput_ISAJson_decoder: Decoder_1[ProcessOutput] = one_of(of_array([map(_arrow1355, Sample_ISAJson_decoder), map(_arrow1356, Data_ISAJson_decoder), map(_arrow1357, Material_ISAJson_decoder)]))

def ARCtrl_Process_ProcessOutput__ProcessOutput_fromISAJsonString_Static_Z721C83C5(s: str) -> ProcessOutput:
    match_value: FSharpResult_2[ProcessOutput, str] = Decode_fromString(ProcessOutput_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_ProcessOutput__ProcessOutput_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ProcessOutput], str]:
    def _arrow1358(f: ProcessOutput, spaces: Any=spaces) -> str:
        value: Json = ProcessOutput_ISAJson_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1358


def ARCtrl_Process_ProcessOutput__ProcessOutput_fromROCrateJsonString_Static_Z721C83C5(s: str) -> ProcessOutput:
    match_value: FSharpResult_2[ProcessOutput, str] = Decode_fromString(ProcessOutput_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_ProcessOutput__ProcessOutput_toROCrateJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ProcessOutput], str]:
    def _arrow1359(f: ProcessOutput, spaces: Any=spaces) -> str:
        value: Json = ProcessOutput_ROCrate_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1359


__all__ = ["ProcessOutput_ROCrate_encoder", "ProcessOutput_ROCrate_decoder", "ProcessOutput_ISAJson_encoder", "ProcessOutput_ISAJson_decoder", "ARCtrl_Process_ProcessOutput__ProcessOutput_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_ProcessOutput__ProcessOutput_toISAJsonString_Static_71136F3F", "ARCtrl_Process_ProcessOutput__ProcessOutput_fromROCrateJsonString_Static_Z721C83C5", "ARCtrl_Process_ProcessOutput__ProcessOutput_toROCrateJsonString_Static_71136F3F"]

