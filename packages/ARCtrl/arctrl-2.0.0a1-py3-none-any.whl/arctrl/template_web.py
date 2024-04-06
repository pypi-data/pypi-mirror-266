from typing import Any
from .fable_modules.fable_library.async_builder import (singleton, Async)
from .fable_modules.fable_library.option import default_arg
from .Json.Table.templates import Templates_fromJsonString
from .WebRequest.web_request import download_file

def get_templates(url: str | None=None) -> Async[Any]:
    url_1: str = default_arg(url, "https://github.com/nfdi4plants/Swate-templates/releases/download/latest/templates.json")
    def _arrow1799(__unit: None=None, url: Any=url) -> Async[Any]:
        def _arrow1798(_arg: str) -> Async[Any]:
            map_result: Any = Templates_fromJsonString(_arg)
            return singleton.Return(map_result)

        return singleton.Bind(download_file(url_1), _arrow1798)

    return singleton.Delay(_arrow1799)


__all__ = ["get_templates"]

