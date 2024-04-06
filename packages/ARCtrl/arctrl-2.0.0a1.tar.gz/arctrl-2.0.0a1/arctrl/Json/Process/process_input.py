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
from ...Core.Process.process_input import ProcessInput
from ...Core.Process.sample import Sample
from ...Core.Process.source import Source
from ..encode import default_spaces
from .data import (Data_ROCrate_encoder, Data_ROCrate_decoder, Data_ISAJson_encoder, Data_ISAJson_decoder)
from .material import (Material_ROCrate_encoder, Material_ROCrate_decoder, Material_ISAJson_encoder, Material_ISAJson_decoder)
from .sample import (Sample_ROCrate_encoder, Sample_ROCrate_decoder, Sample_ISAJson_encoder, Sample_ISAJson_decoder)
from .source import (Source_ROCrate_encoder, Source_ROCrate_decoder, Source_ISAJson_encoder, Source_ISAJson_decoder)

def ProcessInput_ROCrate_encoder(value: ProcessInput) -> Json:
    if value.tag == 1:
        return Sample_ROCrate_encoder(value.fields[0])

    elif value.tag == 2:
        return Data_ROCrate_encoder(value.fields[0])

    elif value.tag == 3:
        return Material_ROCrate_encoder(value.fields[0])

    else: 
        return Source_ROCrate_encoder(value.fields[0])



def _arrow1318(Item: Source) -> ProcessInput:
    return ProcessInput(0, Item)


def _arrow1319(Item_1: Sample) -> ProcessInput:
    return ProcessInput(1, Item_1)


def _arrow1320(Item_2: Data) -> ProcessInput:
    return ProcessInput(2, Item_2)


def _arrow1321(Item_3: Material) -> ProcessInput:
    return ProcessInput(3, Item_3)


ProcessInput_ROCrate_decoder: Decoder_1[ProcessInput] = one_of(of_array([map(_arrow1318, Source_ROCrate_decoder), map(_arrow1319, Sample_ROCrate_decoder), map(_arrow1320, Data_ROCrate_decoder), map(_arrow1321, Material_ROCrate_decoder)]))

def ProcessInput_ISAJson_encoder(value: ProcessInput) -> Json:
    if value.tag == 1:
        return Sample_ISAJson_encoder(value.fields[0])

    elif value.tag == 2:
        return Data_ISAJson_encoder(value.fields[0])

    elif value.tag == 3:
        return Material_ISAJson_encoder(value.fields[0])

    else: 
        return Source_ISAJson_encoder(value.fields[0])



def _arrow1323(Item: Source) -> ProcessInput:
    return ProcessInput(0, Item)


def _arrow1324(Item_1: Sample) -> ProcessInput:
    return ProcessInput(1, Item_1)


def _arrow1327(Item_2: Data) -> ProcessInput:
    return ProcessInput(2, Item_2)


def _arrow1328(Item_3: Material) -> ProcessInput:
    return ProcessInput(3, Item_3)


ProcessInput_ISAJson_decoder: Decoder_1[ProcessInput] = one_of(of_array([map(_arrow1323, Source_ISAJson_decoder), map(_arrow1324, Sample_ISAJson_decoder), map(_arrow1327, Data_ISAJson_decoder), map(_arrow1328, Material_ISAJson_decoder)]))

def ARCtrl_Process_ProcessInput__ProcessInput_fromISAJsonString_Static_Z721C83C5(s: str) -> ProcessInput:
    match_value: FSharpResult_2[ProcessInput, str] = Decode_fromString(ProcessInput_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_ProcessInput__ProcessInput_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ProcessInput], str]:
    def _arrow1329(f: ProcessInput, spaces: Any=spaces) -> str:
        value: Json = ProcessInput_ISAJson_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1329


__all__ = ["ProcessInput_ROCrate_encoder", "ProcessInput_ROCrate_decoder", "ProcessInput_ISAJson_encoder", "ProcessInput_ISAJson_decoder", "ARCtrl_Process_ProcessInput__ProcessInput_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_ProcessInput__ProcessInput_toISAJsonString_Static_71136F3F"]

