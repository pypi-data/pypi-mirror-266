from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ...fable_modules.fable_library.list import (choose, of_array)
from ...fable_modules.fable_library.option import map
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, IOptionalGetter, string, IGetters)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Process.iproperty_value import IPropertyValue_1
from ...Core.Process.value import Value
from ..context.rocrate.property_value_context import context_jsonvalue
from ..encode import try_include

_T = TypeVar("_T")

def gen_id(p: IPropertyValue_1[Any]) -> str:
    match_value: OntologyAnnotation | None = p.GetCategory()
    if match_value is None:
        def _arrow1160(__unit: None=None, p: Any=p) -> str:
            return p.GetAdditionalType()

        return ("#Empty" + str(_arrow1160)) + ""

    else: 
        def _arrow1161(__unit: None=None, p: Any=p) -> str:
            return p.GetAdditionalType()

        return ((((((("" + str(_arrow1161)) + "/") + str(match_value)) + "") + str(p.GetValue())) + "") + str(p.GetUnit())) + ""



def encoder(pv: IPropertyValue_1[Any]) -> Json:
    pattern_input: tuple[str | None, str | None]
    match_value: OntologyAnnotation | None = pv.GetCategory()
    if match_value is None:
        pattern_input = (None, None)

    else: 
        oa: OntologyAnnotation = match_value
        pattern_input = (oa.Name, oa.TermAccessionNumber)

    pattern_input_1: tuple[Json | None, Json | None]
    match_value_1: Value | None = pv.GetValue()
    if match_value_1 is None:
        pattern_input_1 = (None, None)

    else: 
        v: Value = match_value_1
        if v.tag == 1:
            pattern_input_1 = (Json(7, int(v.fields[0]+0x100000000 if v.fields[0] < 0 else v.fields[0])), None)

        elif v.tag == 2:
            pattern_input_1 = (Json(2, v.fields[0]), None)

        elif v.tag == 0:
            oa_1: OntologyAnnotation = v.fields[0]
            def _arrow1162(value_3: str, pv: Any=pv) -> Json:
                return Json(0, value_3)

            def _arrow1163(value_5: str, pv: Any=pv) -> Json:
                return Json(0, value_5)

            pattern_input_1 = (map(_arrow1162, oa_1.Name), map(_arrow1163, oa_1.TermAccessionNumber))

        else: 
            pattern_input_1 = (Json(0, v.fields[0]), None)


    pattern_input_2: tuple[str | None, str | None]
    match_value_2: OntologyAnnotation | None = pv.GetUnit()
    if match_value_2 is None:
        pattern_input_2 = (None, None)

    else: 
        oa_2: OntologyAnnotation = match_value_2
        pattern_input_2 = (oa_2.Name, oa_2.TermAccessionNumber)

    def chooser(tupled_arg: tuple[str, Json], pv: Any=pv) -> tuple[str, Json] | None:
        v_1: Json = tupled_arg[1]
        if equals(v_1, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v_1)


    def _arrow1164(value_11: str, pv: Any=pv) -> Json:
        return Json(0, value_11)

    def _arrow1165(value_13: str, pv: Any=pv) -> Json:
        return Json(0, value_13)

    def _arrow1166(x: Json, pv: Any=pv) -> Json:
        return x

    def _arrow1167(x_1: Json, pv: Any=pv) -> Json:
        return x_1

    def _arrow1168(value_15: str, pv: Any=pv) -> Json:
        return Json(0, value_15)

    def _arrow1169(value_17: str, pv: Any=pv) -> Json:
        return Json(0, value_17)

    return Json(5, choose(chooser, of_array([("@id", Json(0, gen_id(pv))), ("@type", Json(0, "PropertyValue")), ("additionalType", Json(0, pv.GetAdditionalType())), try_include("category", _arrow1164, pattern_input[0]), try_include("categoryCode", _arrow1165, pattern_input[1]), try_include("value", _arrow1166, pattern_input_1[0]), try_include("valueCode", _arrow1167, pattern_input_1[1]), try_include("unit", _arrow1168, pattern_input_2[0]), try_include("unitCode", _arrow1169, pattern_input_2[1]), ("@context", context_jsonvalue)])))


def decoder(create: Callable[[OntologyAnnotation | None, Value | None, OntologyAnnotation | None], _T]) -> Decoder_1[_T]:
    def _arrow1173(get: IGetters, create: Any=create) -> _T:
        def _arrow1170(__unit: None=None) -> OntologyAnnotation | None:
            name: str | None
            object_arg: IOptionalGetter = get.Optional
            name = object_arg.Field("category", string)
            code: str | None
            object_arg_1: IOptionalGetter = get.Optional
            code = object_arg_1.Field("categoryCode", string)
            return None if ((code is None) if (name is None) else False) else OntologyAnnotation.create(name, None, code)

        def _arrow1171(__unit: None=None) -> Value | None:
            value: str | None
            object_arg_2: IOptionalGetter = get.Optional
            value = object_arg_2.Field("value", string)
            code_1: str | None
            object_arg_3: IOptionalGetter = get.Optional
            code_1 = object_arg_3.Field("valueCode", string)
            return None if ((code_1 is None) if (value is None) else False) else Value.from_options(value, None, code_1)

        def _arrow1172(__unit: None=None) -> OntologyAnnotation | None:
            name_1: str | None
            object_arg_4: IOptionalGetter = get.Optional
            name_1 = object_arg_4.Field("unit", string)
            code_2: str | None
            object_arg_5: IOptionalGetter = get.Optional
            code_2 = object_arg_5.Field("unitCode", string)
            return None if ((code_2 is None) if (name_1 is None) else False) else OntologyAnnotation.create(name_1, None, code_2)

        return create(_arrow1170(), _arrow1171(), _arrow1172())

    return object(_arrow1173)


__all__ = ["gen_id", "encoder", "decoder"]

