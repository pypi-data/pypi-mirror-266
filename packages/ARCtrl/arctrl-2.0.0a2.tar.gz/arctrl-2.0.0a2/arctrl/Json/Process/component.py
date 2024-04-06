from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (choose, of_array)
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, IOptionalGetter, IGetters)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Process.component import (Component, Component_createAsPV, Component__get_ComponentName, Component_decomposeName_Z721C83C5)
from ...Core.Process.value import Value
from ..decode import Decode_uri
from ..encode import (try_include, default_spaces)
from ..ontology_annotation import (OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from .property_value import (encoder, decoder as decoder_1)

Component_ROCrate_encoder: Callable[[Component], Json] = encoder

Component_ROCrate_decoder: Decoder_1[Component] = decoder_1(Component_createAsPV)

def Component_ISAJson_encoder(c: Component) -> Json:
    def chooser(tupled_arg: tuple[str, Json], c: Any=c) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1193(value: str, c: Any=c) -> Json:
        return Json(0, value)

    return Json(5, choose(chooser, of_array([try_include("componentName", _arrow1193, Component__get_ComponentName(c)), try_include("componentType", OntologyAnnotation_ISAJson_encoder, c.ComponentType)])))


def _arrow1195(get: IGetters) -> Component:
    name: str | None
    object_arg: IOptionalGetter = get.Optional
    name = object_arg.Field("componentName", Decode_uri)
    pattern_input_1: tuple[Value | None, OntologyAnnotation | None]
    if name is None:
        pattern_input_1 = (None, None)

    else: 
        pattern_input: tuple[Value, OntologyAnnotation | None] = Component_decomposeName_Z721C83C5(name)
        pattern_input_1 = (pattern_input[0], pattern_input[1])

    def _arrow1194(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("componentType", OntologyAnnotation_ISAJson_decoder)

    return Component(pattern_input_1[0], pattern_input_1[1], _arrow1194())


Component_ISAJson_decoder: Decoder_1[Component] = object(_arrow1195)

def ARCtrl_Process_Component__Component_fromISAJsonString_Static_Z721C83C5(s: str) -> Component:
    match_value: FSharpResult_2[Component, str] = Decode_fromString(Component_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Component__Component_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[Component], str]:
    def _arrow1196(f: Component, spaces: Any=spaces) -> str:
        value: Json = Component_ISAJson_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1196


def ARCtrl_Process_Component__Component_fromROCrateJsonString_Static_Z721C83C5(s: str) -> Component:
    match_value: FSharpResult_2[Component, str] = Decode_fromString(Component_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Component__Component_toROCrateJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[Component], str]:
    def _arrow1197(f: Component, spaces: Any=spaces) -> str:
        value: Json = Component_ROCrate_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1197


__all__ = ["Component_ROCrate_encoder", "Component_ROCrate_decoder", "Component_ISAJson_encoder", "Component_ISAJson_decoder", "ARCtrl_Process_Component__Component_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_Component__Component_toISAJsonString_Static_71136F3F", "ARCtrl_Process_Component__Component_fromROCrateJsonString_Static_Z721C83C5", "ARCtrl_Process_Component__Component_toROCrateJsonString_Static_71136F3F"]

