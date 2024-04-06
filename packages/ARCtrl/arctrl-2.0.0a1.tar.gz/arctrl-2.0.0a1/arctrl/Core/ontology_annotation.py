from __future__ import annotations
from typing import Any
from ..fable_modules.fable_library.option import (default_arg, value as value_4)
from ..fable_modules.fable_library.reflection import (TypeInfo, class_type)
from ..fable_modules.fable_library.seq import (to_list, delay, append, singleton, empty, to_array)
from ..fable_modules.fable_library.string_ import (join, to_text, printf)
from ..fable_modules.fable_library.system_text import (StringBuilder__ctor, StringBuilder__Append_Z721C83C5)
from ..fable_modules.fable_library.types import (Array, to_string)
from ..fable_modules.fable_library.util import (ignore, IEnumerable_1)
from .comment import Comment
from .Helper.collections_ import ResizeArray_map
from .Helper.hash_codes import (box_hash_array, box_hash_option, hash_1)
from .Helper.regex import (try_parse_term_annotation, ActivePatterns__007CRegex_007C__007C, Pattern_TermAnnotationShortPattern)

def _expr289() -> TypeInfo:
    return class_type("ARCtrl.OntologyAnnotation", None, OntologyAnnotation)


class OntologyAnnotation:
    def __init__(self, name: str | None=None, tsr: str | None=None, tan: str | None=None, comments: Array[Comment] | None=None) -> None:
        self._name: str | None = name
        self._termSourceREF: str | None = tsr
        self._termAccessionNumber: str | None = tan
        self._comments: Array[Comment] = default_arg(comments, [])

    @property
    def Name(self, __unit: None=None) -> str | None:
        this: OntologyAnnotation = self
        return this._name

    @Name.setter
    def Name(self, name: str | None=None) -> None:
        this: OntologyAnnotation = self
        this._name = name

    @property
    def TermSourceREF(self, __unit: None=None) -> str | None:
        this: OntologyAnnotation = self
        return this._termSourceREF

    @TermSourceREF.setter
    def TermSourceREF(self, tsr: str | None=None) -> None:
        this: OntologyAnnotation = self
        this._termSourceREF = tsr

    @property
    def TermAccessionNumber(self, __unit: None=None) -> str | None:
        this: OntologyAnnotation = self
        return this._termAccessionNumber

    @TermAccessionNumber.setter
    def TermAccessionNumber(self, tan: str | None=None) -> None:
        this: OntologyAnnotation = self
        this._termAccessionNumber = tan

    @property
    def Comments(self, __unit: None=None) -> Array[Comment]:
        this: OntologyAnnotation = self
        return this._comments

    @Comments.setter
    def Comments(self, comments: Array[Comment]) -> None:
        this: OntologyAnnotation = self
        this._comments = comments

    @staticmethod
    def make(name: str | None, tsr: str | None, tan: str | None, comments: Array[Comment]) -> OntologyAnnotation:
        return OntologyAnnotation(name, tsr, tan, comments)

    @staticmethod
    def create(name: str | None=None, tsr: str | None=None, tan: str | None=None, comments: Array[Comment] | None=None) -> OntologyAnnotation:
        comments_1: Array[Comment] = default_arg(comments, [])
        return OntologyAnnotation.make(name, tsr, tan, comments_1)

    @property
    def TANInfo(self, __unit: None=None) -> dict[str, Any] | None:
        this: OntologyAnnotation = self
        match_value: str | None = this.TermAccessionNumber
        return None if (match_value is None) else try_parse_term_annotation(match_value)

    @property
    def NameText(self, __unit: None=None) -> str:
        this: OntologyAnnotation = self
        return default_arg(this.Name, "")

    @staticmethod
    def create_uri_annotation(term_source_ref: str, local_tan: str) -> str:
        return ((((("" + "http://purl.obolibrary.org/obo/") + "") + term_source_ref) + "_") + local_tan) + ""

    @staticmethod
    def from_term_annotation(tan: str) -> OntologyAnnotation:
        r: dict[str, Any] = value_4(try_parse_term_annotation(tan))
        accession: str = (r["IDSpace"] + ":") + r["LocalID"]
        return OntologyAnnotation.create("", r["IDSpace"], accession)

    @property
    def TermAccessionShort(self, __unit: None=None) -> str:
        this: OntologyAnnotation = self
        match_value: dict[str, Any] | None = this.TANInfo
        if match_value is not None:
            id: dict[str, Any] = match_value
            return ((("" + id["IDSpace"]) + ":") + id["LocalID"]) + ""

        else: 
            return ""


    @property
    def TermAccessionOntobeeUrl(self, __unit: None=None) -> str:
        this: OntologyAnnotation = self
        match_value: dict[str, Any] | None = this.TANInfo
        if match_value is not None:
            id: dict[str, Any] = match_value
            return OntologyAnnotation.create_uri_annotation(id["IDSpace"], id["LocalID"])

        else: 
            return ""


    @property
    def TermAccessionAndOntobeeUrlIfShort(self, __unit: None=None) -> str:
        this: OntologyAnnotation = self
        match_value: str | None = this.TermAccessionNumber
        if match_value is not None:
            tan: str = match_value
            return this.TermAccessionOntobeeUrl if (ActivePatterns__007CRegex_007C__007C(Pattern_TermAnnotationShortPattern, tan) is not None) else tan

        else: 
            return ""


    @staticmethod
    def to_string_object(oa: OntologyAnnotation, as_ontobee_purl_url_if_short: bool | None=None) -> dict[str, Any]:
        as_ontobee_purl_url_if_short_1: bool = default_arg(as_ontobee_purl_url_if_short, False)
        TermName: str = default_arg(oa.Name, "")
        TermSourceREF: str = default_arg(oa.TermSourceREF, "")
        def _arrow276(__unit: None=None) -> str:
            url: str = oa.TermAccessionAndOntobeeUrlIfShort
            return default_arg(oa.TermAccessionNumber, "") if (url == "") else url

        return {
            "TermAccessionNumber": _arrow276() if as_ontobee_purl_url_if_short_1 else default_arg(oa.TermAccessionNumber, ""),
            "TermName": TermName,
            "TermSourceREF": TermSourceREF
        }

    def __str__(self, __unit: None=None) -> str:
        this: OntologyAnnotation = self
        sb: Any = StringBuilder__ctor()
        ignore(StringBuilder__Append_Z721C83C5(sb, "{"))
        def _arrow284(__unit: None=None) -> IEnumerable_1[str]:
            def _arrow277(__unit: None=None) -> str:
                arg: str = value_4(this.Name)
                return to_text(printf("Name = %A"))(arg)

            def _arrow283(__unit: None=None) -> IEnumerable_1[str]:
                def _arrow278(__unit: None=None) -> str:
                    arg_1: str = value_4(this.TermSourceREF)
                    return to_text(printf("TSR = %A"))(arg_1)

                def _arrow282(__unit: None=None) -> IEnumerable_1[str]:
                    def _arrow279(__unit: None=None) -> str:
                        arg_2: str = value_4(this.TermAccessionNumber)
                        return to_text(printf("TAN = %A"))(arg_2)

                    def _arrow281(__unit: None=None) -> IEnumerable_1[str]:
                        def _arrow280(__unit: None=None) -> str:
                            arg_3: Array[Comment] = this.Comments
                            return to_text(printf("Comments = %A"))(arg_3)

                        return singleton(_arrow280()) if (len(this.Comments) != 0) else empty()

                    return append(singleton(_arrow279()) if (this.TermAccessionNumber is not None) else empty(), delay(_arrow281))

                return append(singleton(_arrow278()) if (this.TermSourceREF is not None) else empty(), delay(_arrow282))

            return append(singleton(_arrow277()) if (this.Name is not None) else empty(), delay(_arrow283))

        ignore(StringBuilder__Append_Z721C83C5(sb, join("; ", to_list(delay(_arrow284)))))
        ignore(StringBuilder__Append_Z721C83C5(sb, "}"))
        return to_string(sb)

    def __hash__(self, __unit: None=None) -> Any:
        this: OntologyAnnotation = self
        def _arrow288(__unit: None=None) -> IEnumerable_1[Any]:
            def _arrow287(__unit: None=None) -> IEnumerable_1[Any]:
                matchValue: str | None = this.TermSourceREF
                matchValue_1: dict[str, Any] | None = this.TANInfo
                if matchValue is not None:
                    def _arrow285(__unit: None=None) -> IEnumerable_1[Any]:
                        tsr_1: str = matchValue
                        return singleton(box_hash_array([tsr_1, default_arg(this.TermAccessionNumber, "")]))

                    def _arrow286(__unit: None=None) -> IEnumerable_1[Any]:
                        taninfo_1: dict[str, Any] = matchValue_1
                        tsr: str = matchValue
                        return singleton(box_hash_array([tsr, (taninfo_1["IDSpace"] + ":") + taninfo_1["LocalID"]]))

                    return _arrow285() if (matchValue_1 is None) else _arrow286()

                elif matchValue_1 is None:
                    tan_1: str = default_arg(this.TermAccessionNumber, "")
                    return singleton(box_hash_array([default_arg(this.TermAccessionNumber, ""), tan_1]))

                else: 
                    taninfo: dict[str, Any] = matchValue_1
                    return singleton(box_hash_array([taninfo["IDSpace"], (taninfo["IDSpace"] + ":") + taninfo["LocalID"]]))


            return append(singleton(box_hash_option(this.Name)), delay(_arrow287))

        return box_hash_array(to_array(delay(_arrow288)))

    def __eq__(self, obj: Any=None) -> bool:
        this: OntologyAnnotation = self
        return hash_1(this) == hash_1(obj)

    def Copy(self, __unit: None=None) -> OntologyAnnotation:
        this: OntologyAnnotation = self
        def f(c: Comment) -> Comment:
            return c.Copy()

        next_comments: Array[Comment] = ResizeArray_map(f, this.Comments)
        name: str | None = this.Name
        tsr: str | None = this.TermSourceREF
        tan: str | None = this.TermAccessionNumber
        return OntologyAnnotation.make(name, tsr, tan, next_comments)

    def Print(self, __unit: None=None) -> str:
        this: OntologyAnnotation = self
        return to_string(this)

    def PrintCompact(self, __unit: None=None) -> str:
        this: OntologyAnnotation = self
        return "OA " + this.NameText


OntologyAnnotation_reflection = _expr289

def OntologyAnnotation__ctor_Z54349580(name: str | None=None, tsr: str | None=None, tan: str | None=None, comments: Array[Comment] | None=None) -> OntologyAnnotation:
    return OntologyAnnotation(name, tsr, tan, comments)


__all__ = ["OntologyAnnotation_reflection"]

