from __future__ import annotations
from typing import Any
from ..fable_modules.fable_library.list import (choose, of_array)
from ..fable_modules.fable_library.util import equals
from ..fable_modules.thoth_json_core.decode import (object, IOptionalGetter, IGetters)
from ..fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ..Core.arc_types import ArcInvestigation
from .context.rocrate.rocrate_context import (conforms_to_jsonvalue, context_jsonvalue)
from .encode import try_include
from .investigation import (Investigation_ROCrate_encoder, Investigation_ROCrate_decoder)

def encoder(isa: ArcInvestigation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], isa: Any=isa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1659(value: str, isa: Any=isa) -> Json:
        return Json(0, value)

    def _arrow1660(value_2: str, isa: Any=isa) -> Json:
        return Json(0, value_2)

    def _arrow1661(oa: ArcInvestigation, isa: Any=isa) -> Json:
        return Investigation_ROCrate_encoder(oa)

    return Json(5, choose(chooser, of_array([try_include("@type", _arrow1659, "CreativeWork"), try_include("@id", _arrow1660, "ro-crate-metadata.json"), try_include("about", _arrow1661, isa), ("conformsTo", conforms_to_jsonvalue), ("@context", context_jsonvalue)])))


def _arrow1662(get: IGetters) -> ArcInvestigation | None:
    object_arg: IOptionalGetter = get.Optional
    return object_arg.Field("about", Investigation_ROCrate_decoder)


decoder: Decoder_1[ArcInvestigation | None] = object(_arrow1662)

__all__ = ["encoder", "decoder"]

