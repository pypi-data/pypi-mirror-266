from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from ..fable_library.list import FSharpList
from ..fable_library.reflection import (TypeInfo, union_type, string_type, class_type, list_type, bool_type, option_type, int32_type, record_type, obj_type)
from ..fable_library.types import (Array, Union, Record)

def _expr0() -> TypeInfo:
    return union_type("Fable.SimpleHttp.HttpMethod", [], HttpMethod, lambda: [[], [], [], [], [], [], []])


class HttpMethod(Union):
    def __init__(self, tag: int, *fields: Any) -> None:
        super().__init__()
        self.tag: int = tag or 0
        self.fields: Array[Any] = list(fields)

    @staticmethod
    def cases() -> list[str]:
        return ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]


HttpMethod_reflection = _expr0

def _expr1() -> TypeInfo:
    return union_type("Fable.SimpleHttp.Header", [], Header, lambda: [[("Item1", string_type), ("Item2", string_type)]])


class Header(Union):
    def __init__(self, tag: int, *fields: Any) -> None:
        super().__init__()
        self.tag: int = tag or 0
        self.fields: Array[Any] = list(fields)

    @staticmethod
    def cases() -> list[str]:
        return ["Header"]


Header_reflection = _expr1

def _expr2() -> TypeInfo:
    return union_type("Fable.SimpleHttp.BodyContent", [], BodyContent, lambda: [[], [("Item", string_type)], [("Item", class_type("Browser.Types.Blob"))], [("Item", class_type("Browser.Types.FormData"))]])


class BodyContent(Union):
    def __init__(self, tag: int, *fields: Any) -> None:
        super().__init__()
        self.tag: int = tag or 0
        self.fields: Array[Any] = list(fields)

    @staticmethod
    def cases() -> list[str]:
        return ["Empty", "Text", "Binary", "Form"]


BodyContent_reflection = _expr2

def _expr3() -> TypeInfo:
    return union_type("Fable.SimpleHttp.ResponseTypes", [], ResponseTypes, lambda: [[], [], []])


class ResponseTypes(Union):
    def __init__(self, tag: int, *fields: Any) -> None:
        super().__init__()
        self.tag: int = tag or 0
        self.fields: Array[Any] = list(fields)

    @staticmethod
    def cases() -> list[str]:
        return ["Text", "Blob", "ArrayBuffer"]


ResponseTypes_reflection = _expr3

def _expr4() -> TypeInfo:
    return record_type("Fable.SimpleHttp.HttpRequest", [], HttpRequest, lambda: [("url", string_type), ("method", HttpMethod_reflection()), ("headers", list_type(Header_reflection())), ("with_credentials", bool_type), ("overriden_mime_type", option_type(string_type)), ("overriden_response_type", option_type(ResponseTypes_reflection())), ("timeout", option_type(int32_type)), ("content", BodyContent_reflection())])


@dataclass(eq = False, repr = False, slots = True)
class HttpRequest(Record):
    url: str
    method: HttpMethod
    headers: FSharpList[Header]
    with_credentials: bool
    overriden_mime_type: str | None
    overriden_response_type: ResponseTypes | None
    timeout: int | None
    content: BodyContent

HttpRequest_reflection = _expr4

def _expr5() -> TypeInfo:
    return union_type("Fable.SimpleHttp.ResponseContent", [], ResponseContent, lambda: [[("Item", string_type)], [("Item", class_type("Browser.Types.Blob"))], [("Item", class_type("Fable.Core.JS.ArrayBuffer"))], [("Item", obj_type)]])


class ResponseContent(Union):
    def __init__(self, tag: int, *fields: Any) -> None:
        super().__init__()
        self.tag: int = tag or 0
        self.fields: Array[Any] = list(fields)

    @staticmethod
    def cases() -> list[str]:
        return ["Text", "Blob", "ArrayBuffer", "Unknown"]


ResponseContent_reflection = _expr5

def _expr6() -> TypeInfo:
    return record_type("Fable.SimpleHttp.HttpResponse", [], HttpResponse, lambda: [("status_code", int32_type), ("response_text", string_type), ("response_type", string_type), ("response_url", string_type), ("response_headers", class_type("Microsoft.FSharp.Collections.FSharpMap`2", [string_type, string_type])), ("content", ResponseContent_reflection())])


@dataclass(eq = False, repr = False, slots = True)
class HttpResponse(Record):
    status_code: int
    response_text: str
    response_type: str
    response_url: str
    response_headers: Any
    content: ResponseContent

HttpResponse_reflection = _expr6

__all__ = ["HttpMethod_reflection", "Header_reflection", "BodyContent_reflection", "ResponseTypes_reflection", "HttpRequest_reflection", "ResponseContent_reflection", "HttpResponse_reflection"]

