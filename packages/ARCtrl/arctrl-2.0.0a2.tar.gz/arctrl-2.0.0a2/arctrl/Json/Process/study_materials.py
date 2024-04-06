from __future__ import annotations
from typing import Any
from ...fable_modules.fable_library.list import (FSharpList, choose, of_array)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.types import Json
from ...Core.Process.material import Material
from ...Core.Process.process import Process
from ...Core.Process.process_sequence import (get_sources, get_samples, get_materials)
from ...Core.Process.sample import Sample
from ...Core.Process.source import Source
from ..encode import try_include_list
from .material import Material_ISAJson_encoder
from .sample import Sample_ISAJson_encoder
from .source import Source_ISAJson_encoder

def encoder(ps: FSharpList[Process]) -> Json:
    source: FSharpList[Source] = get_sources(ps)
    samples: FSharpList[Sample] = get_samples(ps)
    materials: FSharpList[Material] = get_materials(ps)
    def chooser(tupled_arg: tuple[str, Json], ps: Any=ps) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1367(oa: Source, ps: Any=ps) -> Json:
        return Source_ISAJson_encoder(oa)

    def _arrow1368(oa_1: Sample, ps: Any=ps) -> Json:
        return Sample_ISAJson_encoder(oa_1)

    def _arrow1369(oa_2: Material, ps: Any=ps) -> Json:
        return Material_ISAJson_encoder(oa_2)

    return Json(5, choose(chooser, of_array([try_include_list("sources", _arrow1367, source), try_include_list("samples", _arrow1368, samples), try_include_list("otherMaterials", _arrow1369, materials)])))


__all__ = ["encoder"]

