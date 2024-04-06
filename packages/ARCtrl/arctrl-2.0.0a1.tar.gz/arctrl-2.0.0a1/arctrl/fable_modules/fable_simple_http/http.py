from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..fable_library.array_ import choose
from ..fable_library.async_ import from_continuations
from ..fable_library.async_builder import (Async, singleton as singleton_1)
from ..fable_library.list import (empty, append, singleton, FSharpList, of_array as of_array_1, is_empty, head, tail)
from ..fable_library.map import (empty as empty_1, of_array)
from ..fable_library.option import some
from ..fable_library.string_ import (is_null_or_empty, split, join)
from ..fable_library.types import Array
from ..fable_library.util import (ignore, compare_primitives, get_enumerator)
from .types import (Header, HttpMethod, BodyContent, HttpRequest, ResponseContent, HttpResponse, ResponseTypes)

def Blob_download(blob: Blob, file_name: str) -> None:
    element: HTMLAnchorElement = document.create_element("a")
    element.target = "_blank"
    element.href = window.URL.createObjectURL(blob)
    element.set_attribute("download", file_name)
    ignore(document.body.append_child(element))
    element.click()
    ignore(document.body.remove_child(element))


def FileReader_readBlobAsText(blob: Blob) -> Async[str]:
    def callback(tupled_arg: tuple[Callable[[str], None], Callable[[Exception], None], Callable[[Any], None]], blob: Any=blob) -> None:
        reader: FileReader = FileReader()
        def _arrow7(_arg_2: Event, tupled_arg: Any=tupled_arg) -> None:
            if reader.ready_state == 2:
                tupled_arg[0](reader.result)


        reader.onload = _arrow7
        reader.read_as_text(blob)

    return from_continuations(callback)


def FileReader_readFileAsText(file: File) -> Async[str]:
    def callback(tupled_arg: tuple[Callable[[str], None], Callable[[Exception], None], Callable[[Any], None]], file: Any=file) -> None:
        reader: FileReader = FileReader()
        def _arrow8(_arg_2: Event, tupled_arg: Any=tupled_arg) -> None:
            if reader.ready_state == 2:
                tupled_arg[0](reader.result)


        reader.onload = _arrow8
        reader.read_as_text(file)

    return from_continuations(callback)


def FormData_append(key: str, value: str, form: FormData) -> FormData:
    form.append(key, value)
    return form


def FormData_appendFile(key: str, file: File, form: FormData) -> FormData:
    form.append(key, file)
    return form


def FormData_appendNamedFile(key: str, file_name: str, file: File, form: FormData) -> FormData:
    form.append(key, file, file_name)
    return form


def FormData_appendBlob(key: str, blob: Blob, form: FormData) -> FormData:
    form.append(key, blob)
    return form


def FormData_appendNamedBlob(key: str, file_name: str, blob: Blob, form: FormData) -> FormData:
    form.append(key, blob, file_name)
    return form


def Headers_contentType(value: str) -> Header:
    return Header(0, "Content-Type", value)


def Headers_accept(value: str) -> Header:
    return Header(0, "Accept", value)


def Headers_acceptCharset(value: str) -> Header:
    return Header(0, "Accept-Charset", value)


def Headers_acceptEncoding(value: str) -> Header:
    return Header(0, "Accept-Encoding", value)


def Headers_acceptLanguage(value: str) -> Header:
    return Header(0, "Accept-Language", value)


def Headers_acceptDateTime(value: str) -> Header:
    return Header(0, "Accept-Datetime", value)


def Headers_authorization(value: str) -> Header:
    return Header(0, "Authorization", value)


def Headers_cacheControl(value: str) -> Header:
    return Header(0, "Cache-Control", value)


def Headers_connection(value: str) -> Header:
    return Header(0, "Connection", value)


def Headers_cookie(value: str) -> Header:
    return Header(0, "Cookie", value)


def Headers_contentMD5(value: str) -> Header:
    return Header(0, "Content-MD5", value)


def Headers_date(value: str) -> Header:
    return Header(0, "Date", value)


def Headers_expect(value: str) -> Header:
    return Header(0, "Expect", value)


def Headers_ifMatch(value: str) -> Header:
    return Header(0, "If-Match", value)


def Headers_ifModifiedSince(value: str) -> Header:
    return Header(0, "If-Modified-Since", value)


def Headers_ifNoneMatch(value: str) -> Header:
    return Header(0, "If-None-Match", value)


def Headers_ifRange(value: str) -> Header:
    return Header(0, "If-Range", value)


def Headers_IfUnmodifiedSince(value: str) -> Header:
    return Header(0, "If-Unmodified-Since", value)


def Headers_maxForwards(value: str) -> Header:
    return Header(0, "Max-Forwards", value)


def Headers_origin(value: str) -> Header:
    return Header(0, "Origin", value)


def Headers_pragma(value: str) -> Header:
    return Header(0, "Pragma", value)


def Headers_proxyAuthorization(value: str) -> Header:
    return Header(0, "Proxy-Authorization", value)


def Headers_range(value: str) -> Header:
    return Header(0, "Range", value)


def Headers_referer(value: str) -> Header:
    return Header(0, "Referer", value)


def Headers_userAgent(value: str) -> Header:
    return Header(0, "User-Agent", value)


def Headers_create(key: str, value: str) -> Header:
    return Header(0, key, value)


Http_defaultRequest: HttpRequest = HttpRequest("", HttpMethod(0), empty(), False, None, None, None, BodyContent(0))

class ObjectExpr9:
    @property
    def Compare(self) -> Callable[[str, str], int]:
        return compare_primitives


Http_emptyResponse: HttpResponse = HttpResponse(0, "", "", "", empty_1(ObjectExpr9()), ResponseContent(0, ""))

def Http_splitAt(delimiter: str, input: str) -> Array[str]:
    if is_null_or_empty(input):
        return [input]

    else: 
        return split(input, [delimiter], None, 0)



def Http_serializeMethod(_arg: HttpMethod) -> str:
    if _arg.tag == 1:
        return "POST"

    elif _arg.tag == 3:
        return "PATCH"

    elif _arg.tag == 2:
        return "PUT"

    elif _arg.tag == 4:
        return "DELETE"

    elif _arg.tag == 6:
        return "OPTIONS"

    elif _arg.tag == 5:
        return "HEAD"

    else: 
        return "GET"



def Http_request(url: str) -> HttpRequest:
    return HttpRequest(url, Http_defaultRequest.method, Http_defaultRequest.headers, Http_defaultRequest.with_credentials, Http_defaultRequest.overriden_mime_type, Http_defaultRequest.overriden_response_type, Http_defaultRequest.timeout, Http_defaultRequest.content)


def Http_method(http_verb: HttpMethod, req: HttpRequest) -> HttpRequest:
    return HttpRequest(req.url, http_verb, req.headers, req.with_credentials, req.overriden_mime_type, req.overriden_response_type, req.timeout, req.content)


def Http_header(single_header: Header, req: HttpRequest) -> HttpRequest:
    return HttpRequest(req.url, req.method, append(req.headers, singleton(single_header)), req.with_credentials, req.overriden_mime_type, req.overriden_response_type, req.timeout, req.content)


def Http_headers(values: FSharpList[Header], req: HttpRequest) -> HttpRequest:
    return HttpRequest(req.url, req.method, append(req.headers, values), req.with_credentials, req.overriden_mime_type, req.overriden_response_type, req.timeout, req.content)


def Http_withCredentials(enabled: bool, req: HttpRequest) -> HttpRequest:
    return HttpRequest(req.url, req.method, req.headers, enabled, req.overriden_mime_type, req.overriden_response_type, req.timeout, req.content)


def Http_withTimeout(timeout_in_milliseconds: int, req: HttpRequest) -> HttpRequest:
    return HttpRequest(req.url, req.method, req.headers, req.with_credentials, req.overriden_mime_type, req.overriden_response_type, timeout_in_milliseconds, req.content)


def Http_overrideMimeType(value: str, req: HttpRequest) -> HttpRequest:
    return HttpRequest(req.url, req.method, req.headers, req.with_credentials, value, req.overriden_response_type, req.timeout, req.content)


def Http_overrideResponseType(value: ResponseTypes, req: HttpRequest) -> HttpRequest:
    return HttpRequest(req.url, req.method, req.headers, req.with_credentials, req.overriden_mime_type, value, req.timeout, req.content)


def Http_content(body_content: BodyContent, req: HttpRequest) -> HttpRequest:
    return HttpRequest(req.url, req.method, req.headers, req.with_credentials, req.overriden_mime_type, req.overriden_response_type, req.timeout, body_content)


def Http_send(req: HttpRequest) -> Async[HttpResponse]:
    def callback(tupled_arg: tuple[Callable[[HttpResponse], None], Callable[[Exception], None], Callable[[Any], None]], req: Any=req) -> None:
        xhr: XMLHttpRequest = XMLHttpRequest()
        xhr.open(Http_serializeMethod(req.method), req.url)
        def _arrow15(__unit: None=None, tupled_arg: Any=tupled_arg) -> None:
            if xhr.ready_state == 4:
                def _arrow14(__unit: None=None) -> HttpResponse:
                    response_text: str
                    match_value: str = xhr.response_type
                    response_text = xhr.response_text if (match_value == "") else (xhr.response_text if (match_value == "text") else "")
                    status_code: int = xhr.status or 0
                    response_type: str = xhr.response_type
                    content: ResponseContent
                    match_value_1: str = xhr.response_type
                    (pattern_matching_result,) = (None,)
                    if match_value_1 == "":
                        pattern_matching_result = 0

                    elif match_value_1 == "text":
                        pattern_matching_result = 0

                    elif match_value_1 == "arraybuffer":
                        pattern_matching_result = 1

                    elif match_value_1 == "blob":
                        pattern_matching_result = 2

                    else: 
                        pattern_matching_result = 3

                    if pattern_matching_result == 0:
                        content = ResponseContent(0, xhr.response_text)

                    elif pattern_matching_result == 1:
                        content = ResponseContent(2, xhr.response)

                    elif pattern_matching_result == 2:
                        content = ResponseContent(1, xhr.response)

                    elif pattern_matching_result == 3:
                        content = ResponseContent(3, xhr.response)

                    def chooser(header_line: str) -> tuple[str, str] | None:
                        match_value_2: FSharpList[str] = of_array_1(Http_splitAt(":", header_line))
                        if not is_empty(match_value_2):
                            return (head(match_value_2).lower(), join(":", tail(match_value_2)).strip())

                        else: 
                            return None


                    class ObjectExpr13:
                        @property
                        def Compare(self) -> Callable[[str, str], int]:
                            return compare_primitives

                    response_headers: Any = of_array(choose(chooser, Http_splitAt("\r\n", xhr.get_all_response_headers()), None), ObjectExpr13())
                    return HttpResponse(status_code, response_text, response_type, xhr.response_url, response_headers, content)

                tupled_arg[0](_arrow14())


        xhr.onreadystatechange = _arrow15
        with get_enumerator(req.headers) as enumerator:
            while enumerator.System_Collections_IEnumerator_MoveNext():
                for_loop_var: Header = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                xhr.set_request_header(for_loop_var.fields[0], for_loop_var.fields[1])
        xhr.with_credentials = req.with_credentials
        match_value_3: str | None = req.overriden_mime_type
        if match_value_3 is None:
            pass

        else: 
            mime_type: str = match_value_3
            xhr.override_mime_type(mime_type)

        match_value_4: ResponseTypes | None = req.overriden_response_type
        if match_value_4 is None:
            pass

        elif match_value_4.tag == 1:
            xhr.response_type = "blob"

        elif match_value_4.tag == 2:
            xhr.response_type = "arraybuffer"

        else: 
            xhr.response_type = "text"

        match_value_5: int | None = req.timeout
        if match_value_5 is None:
            pass

        else: 
            timeout: int = match_value_5 or 0
            xhr.timeout = timeout or 0

        match_value_6: BodyContent = req.content
        if match_value_6.tag == 1:
            xhr.send(some(match_value_6.fields[0]))

        elif match_value_6.tag == 3:
            xhr.send(some(match_value_6.fields[0]))

        elif match_value_6.tag == 2:
            xhr.send(some(match_value_6.fields[0]))

        else: 
            xhr.send()


    return from_continuations(callback)


def Http_get(url: str) -> Async[tuple[int, str]]:
    def _arrow17(__unit: None=None, url: Any=url) -> Async[tuple[int, str]]:
        def _arrow16(_arg: HttpResponse) -> Async[tuple[int, str]]:
            response: HttpResponse = _arg
            return singleton_1.Return((response.status_code, response.response_text))

        return singleton_1.Bind(Http_send(Http_method(HttpMethod(0), Http_request(url))), _arrow16)

    return singleton_1.Delay(_arrow17)


def Http_put(url: str, data: str) -> Async[tuple[int, str]]:
    def _arrow19(__unit: None=None, url: Any=url, data: Any=data) -> Async[tuple[int, str]]:
        def _arrow18(_arg: HttpResponse) -> Async[tuple[int, str]]:
            response: HttpResponse = _arg
            return singleton_1.Return((response.status_code, response.response_text))

        return singleton_1.Bind(Http_send(Http_content(BodyContent(1, data), Http_method(HttpMethod(2), Http_request(url)))), _arrow18)

    return singleton_1.Delay(_arrow19)


def Http_delete(url: str) -> Async[tuple[int, str]]:
    def _arrow21(__unit: None=None, url: Any=url) -> Async[tuple[int, str]]:
        def _arrow20(_arg: HttpResponse) -> Async[tuple[int, str]]:
            response: HttpResponse = _arg
            return singleton_1.Return((response.status_code, response.response_text))

        return singleton_1.Bind(Http_send(Http_method(HttpMethod(4), Http_request(url))), _arrow20)

    return singleton_1.Delay(_arrow21)


def Http_patch(url: str, data: str) -> Async[tuple[int, str]]:
    def _arrow23(__unit: None=None, url: Any=url, data: Any=data) -> Async[tuple[int, str]]:
        def _arrow22(_arg: HttpResponse) -> Async[tuple[int, str]]:
            response: HttpResponse = _arg
            return singleton_1.Return((response.status_code, response.response_text))

        return singleton_1.Bind(Http_send(Http_content(BodyContent(1, data), Http_method(HttpMethod(3), Http_request(url)))), _arrow22)

    return singleton_1.Delay(_arrow23)


def Http_post(url: str, data: str) -> Async[tuple[int, str]]:
    def _arrow25(__unit: None=None, url: Any=url, data: Any=data) -> Async[tuple[int, str]]:
        def _arrow24(_arg: HttpResponse) -> Async[tuple[int, str]]:
            response: HttpResponse = _arg
            return singleton_1.Return((response.status_code, response.response_text))

        return singleton_1.Bind(Http_send(Http_content(BodyContent(1, data), Http_method(HttpMethod(1), Http_request(url)))), _arrow24)

    return singleton_1.Delay(_arrow25)


__all__ = ["Blob_download", "FileReader_readBlobAsText", "FileReader_readFileAsText", "FormData_append", "FormData_appendFile", "FormData_appendNamedFile", "FormData_appendBlob", "FormData_appendNamedBlob", "Headers_contentType", "Headers_accept", "Headers_acceptCharset", "Headers_acceptEncoding", "Headers_acceptLanguage", "Headers_acceptDateTime", "Headers_authorization", "Headers_cacheControl", "Headers_connection", "Headers_cookie", "Headers_contentMD5", "Headers_date", "Headers_expect", "Headers_ifMatch", "Headers_ifModifiedSince", "Headers_ifNoneMatch", "Headers_ifRange", "Headers_IfUnmodifiedSince", "Headers_maxForwards", "Headers_origin", "Headers_pragma", "Headers_proxyAuthorization", "Headers_range", "Headers_referer", "Headers_userAgent", "Headers_create", "Http_defaultRequest", "Http_emptyResponse", "Http_splitAt", "Http_serializeMethod", "Http_request", "Http_method", "Http_header", "Http_headers", "Http_withCredentials", "Http_withTimeout", "Http_overrideMimeType", "Http_overrideResponseType", "Http_content", "Http_send", "Http_get", "Http_put", "Http_delete", "Http_patch", "Http_post"]

