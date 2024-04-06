from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ...fable_modules.fable_library.array_ import map
from ...fable_modules.fable_library.reflection import (name, get_union_cases, TypeInfo, string_type, union_type)
from ...fable_modules.fable_library.reg_exp import (get_item, groups)
from ...fable_modules.fable_library.string_ import (to_fail, printf)
from ...fable_modules.fable_library.types import (Array, to_string, Union)
from ...fable_modules.fable_library.util import equals
from ..Helper.regex import (try_parse_iotype_header, ActivePatterns__007CRegex_007C__007C, Pattern_InputPattern, Pattern_OutputPattern, ActivePatterns__007CTermColumn_007C__007C)
from ..ontology_annotation import (OntologyAnnotation, OntologyAnnotation_reflection)

__A = TypeVar("__A")

def _expr386() -> TypeInfo:
    return union_type("ARCtrl.IOType", [], IOType, lambda: [[], [], [], [], [], [], [("Item", string_type)]])


class IOType(Union):
    def __init__(self, tag: int, *fields: Any) -> None:
        super().__init__()
        self.tag: int = tag or 0
        self.fields: Array[Any] = list(fields)

    @staticmethod
    def cases() -> list[str]:
        return ["Source", "Sample", "RawDataFile", "DerivedDataFile", "ImageFile", "Material", "FreeText"]

    @staticmethod
    def All() -> Array[IOType]:
        return [IOType(0), IOType(1), IOType(2), IOType(3), IOType(4), IOType(5)]

    @staticmethod
    def Cases() -> Array[tuple[int, str]]:
        def mapping(x: Any) -> tuple[int, str]:
            return (x.tag, name(x))

        return map(mapping, get_union_cases(IOType_reflection()), None)

    @property
    def as_input(self, __unit: None=None) -> str:
        this: IOType = self
        def string_create(x: Any | None=None) -> str:
            def _arrow384(__unit: None=None, x: Any=x) -> str:
                copy_of_struct: __A = x
                return to_string(copy_of_struct)

            return ("Input [" + _arrow384()) + "]"

        return string_create(this.fields[0]) if (this.tag == 6) else string_create(this)

    @property
    def as_output(self, __unit: None=None) -> str:
        this: IOType = self
        def string_create(x: Any | None=None) -> str:
            def _arrow385(__unit: None=None, x: Any=x) -> str:
                copy_of_struct: __A = x
                return to_string(copy_of_struct)

            return ("Output [" + _arrow385()) + "]"

        return string_create(this.fields[0]) if (this.tag == 6) else string_create(this)

    def Merge(self, other: IOType) -> IOType:
        this: IOType = self
        if this.tag == 4:
            if other.tag == 0:
                return IOType(4)

            elif other.tag == 2:
                return IOType(4)

            elif other.tag == 3:
                return IOType(4)

            elif other.tag == 4:
                return IOType(4)

            else: 
                raise Exception(("ImageFile IO column and " + str(other)) + " can not be merged")


        elif this.tag == 3:
            if other.tag == 0:
                return IOType(3)

            elif other.tag == 2:
                return IOType(3)

            elif other.tag == 3:
                return IOType(3)

            elif other.tag == 4:
                return IOType(4)

            else: 
                raise Exception(("DerivedDataFile IO column and " + str(other)) + " can not be merged")


        elif this.tag == 2:
            if other.tag == 0:
                return IOType(2)

            elif other.tag == 2:
                return IOType(2)

            elif other.tag == 3:
                return IOType(3)

            elif other.tag == 4:
                return IOType(4)

            else: 
                raise Exception(("RawDataFile IO column and " + str(other)) + " can not be merged")


        elif this.tag == 1:
            if other.tag == 0:
                return IOType(1)

            elif other.tag == 1:
                return IOType(1)

            else: 
                raise Exception(("Sample IO column and " + str(other)) + " can not be merged")


        elif this.tag == 0:
            return IOType(0) if (other.tag == 0) else other

        elif this.tag == 5:
            if other.tag == 0:
                return IOType(5)

            elif other.tag == 5:
                return IOType(5)

            else: 
                raise Exception(("Material IO column and " + str(other)) + " can not be merged")


        elif other.tag == 6:
            if this.fields[0] == other.fields[0]:
                return IOType(6, this.fields[0])

            else: 
                raise Exception(((("FreeText IO column names " + this.fields[0]) + " and ") + other.fields[0]) + " do differ")


        else: 
            raise Exception(("FreeText IO column and " + str(other)) + " can not be merged")


    def __str__(self, __unit: None=None) -> str:
        this: IOType = self
        if this.tag == 1:
            return "Sample Name"

        elif this.tag == 2:
            return "Raw Data File"

        elif this.tag == 3:
            return "Derived Data File"

        elif this.tag == 4:
            return "Image File"

        elif this.tag == 5:
            return "Material"

        elif this.tag == 6:
            return this.fields[0]

        else: 
            return "Source Name"


    @staticmethod
    def of_string(str_1: str) -> IOType:
        return IOType(0) if (str_1 == "Source") else (IOType(0) if (str_1 == "Source Name") else (IOType(1) if (str_1 == "Sample") else (IOType(1) if (str_1 == "Sample Name") else (IOType(2) if (str_1 == "RawDataFile") else (IOType(2) if (str_1 == "Raw Data File") else (IOType(3) if (str_1 == "DerivedDataFile") else (IOType(3) if (str_1 == "Derived Data File") else (IOType(4) if (str_1 == "ImageFile") else (IOType(4) if (str_1 == "Image File") else (IOType(5) if (str_1 == "Material") else IOType(6, str_1)))))))))))

    @staticmethod
    def try_of_header_string(str_1: str) -> IOType | None:
        match_value: str | None = try_parse_iotype_header(str_1)
        if match_value is None:
            return None

        else: 
            s: str = match_value
            return IOType.of_string(s)


    def GetUITooltip(self, __unit: None=None) -> str:
        this: IOType = self
        return IOType.get_uitooltip(this)

    @staticmethod
    def get_uitooltip(iotype: Any) -> str:
        (pattern_matching_result,) = (None,)
        if str(type(iotype)) == "<class \'str\'>":
            if equals(iotype, "Source"):
                pattern_matching_result = 0

            elif equals(iotype, "Sample"):
                pattern_matching_result = 1

            elif equals(iotype, "RawDataFile"):
                pattern_matching_result = 2

            elif equals(iotype, "DerivedDataFile"):
                pattern_matching_result = 3

            elif equals(iotype, "ImageFile"):
                pattern_matching_result = 4

            elif equals(iotype, "Material"):
                pattern_matching_result = 5

            elif equals(iotype, "FreeText"):
                pattern_matching_result = 6

            else: 
                pattern_matching_result = 7


        elif iotype.tag == 1:
            pattern_matching_result = 1

        elif iotype.tag == 2:
            pattern_matching_result = 2

        elif iotype.tag == 3:
            pattern_matching_result = 3

        elif iotype.tag == 4:
            pattern_matching_result = 4

        elif iotype.tag == 5:
            pattern_matching_result = 5

        elif iotype.tag == 6:
            pattern_matching_result = 6

        else: 
            pattern_matching_result = 0

        if pattern_matching_result == 0:
            return "The source value must be a unique identifier for an organism or a sample."

        elif pattern_matching_result == 1:
            return "The Sample Name column describes specifc laboratory samples with a unique identifier."

        elif pattern_matching_result == 2:
            return "The Raw Data File column defines untransformed and unprocessed data files."

        elif pattern_matching_result == 3:
            return "The Derived Data File column defines transformed and/or processed data files."

        elif pattern_matching_result == 4:
            return "Placeholder"

        elif pattern_matching_result == 5:
            return "Placeholder"

        elif pattern_matching_result == 6:
            return "Placeholder"

        elif pattern_matching_result == 7:
            raise Exception(("Unable to parse combination to existing IOType: `" + str(iotype)) + "`")


    @staticmethod
    def source(__unit: None=None) -> IOType:
        return IOType(0)

    @staticmethod
    def sample(__unit: None=None) -> IOType:
        return IOType(1)

    @staticmethod
    def raw_data_file(__unit: None=None) -> IOType:
        return IOType(2)

    @staticmethod
    def derived_data_file(__unit: None=None) -> IOType:
        return IOType(3)

    @staticmethod
    def image_file(__unit: None=None) -> IOType:
        return IOType(4)

    @staticmethod
    def material(__unit: None=None) -> IOType:
        return IOType(5)

    @staticmethod
    def free_text(s: str) -> IOType:
        return IOType(6, s)


IOType_reflection = _expr386

def _expr387() -> TypeInfo:
    return union_type("ARCtrl.CompositeHeader", [], CompositeHeader, lambda: [[("Item", OntologyAnnotation_reflection())], [("Item", OntologyAnnotation_reflection())], [("Item", OntologyAnnotation_reflection())], [("Item", OntologyAnnotation_reflection())], [], [], [], [], [], [], [], [("Item", IOType_reflection())], [("Item", IOType_reflection())], [("Item", string_type)]])


class CompositeHeader(Union):
    def __init__(self, tag: int, *fields: Any) -> None:
        super().__init__()
        self.tag: int = tag or 0
        self.fields: Array[Any] = list(fields)

    @staticmethod
    def cases() -> list[str]:
        return ["Component", "Characteristic", "Factor", "Parameter", "ProtocolType", "ProtocolDescription", "ProtocolUri", "ProtocolVersion", "ProtocolREF", "Performer", "Date", "Input", "Output", "FreeText"]

    @staticmethod
    def Cases() -> Array[tuple[int, str]]:
        def mapping(x: Any) -> tuple[int, str]:
            return (x.tag, name(x))

        return map(mapping, get_union_cases(CompositeHeader_reflection()), None)

    @staticmethod
    def js_get_column_meta_type(inp: int) -> int:
        return 1 if (inp == 0) else (1 if (inp == 1) else (1 if (inp == 2) else (1 if (inp == 3) else (0 if (inp == 4) else (0 if (inp == 5) else (0 if (inp == 6) else (0 if (inp == 7) else (0 if (inp == 8) else (0 if (inp == 9) else (0 if (inp == 10) else (2 if (inp == 11) else (2 if (inp == 12) else (3 if (inp == 13) else to_fail(printf("Cannot assign input `Tag` (%i) to `CompositeHeader`"))(inp))))))))))))))

    def __str__(self, __unit: None=None) -> str:
        this: CompositeHeader = self
        if this.tag == 2:
            return ("Factor [" + this.fields[0].NameText) + "]"

        elif this.tag == 1:
            return ("Characteristic [" + this.fields[0].NameText) + "]"

        elif this.tag == 0:
            return ("Component [" + this.fields[0].NameText) + "]"

        elif this.tag == 4:
            return "Protocol Type"

        elif this.tag == 8:
            return "Protocol REF"

        elif this.tag == 5:
            return "Protocol Description"

        elif this.tag == 6:
            return "Protocol Uri"

        elif this.tag == 7:
            return "Protocol Version"

        elif this.tag == 9:
            return "Performer"

        elif this.tag == 10:
            return "Date"

        elif this.tag == 11:
            return this.fields[0].as_input

        elif this.tag == 12:
            return this.fields[0].as_output

        elif this.tag == 13:
            return this.fields[0]

        else: 
            return ("Parameter [" + this.fields[0].NameText) + "]"


    def ToTerm(self, __unit: None=None) -> OntologyAnnotation:
        this: CompositeHeader = self
        if this.tag == 2:
            return this.fields[0]

        elif this.tag == 1:
            return this.fields[0]

        elif this.tag == 0:
            return this.fields[0]

        elif this.tag == 4:
            return OntologyAnnotation.create(to_string(this), None, this.GetFeaturedColumnAccession)

        elif this.tag == 8:
            return OntologyAnnotation.create(to_string(this))

        elif this.tag == 5:
            return OntologyAnnotation.create(to_string(this))

        elif this.tag == 6:
            return OntologyAnnotation.create(to_string(this))

        elif this.tag == 7:
            return OntologyAnnotation.create(to_string(this))

        elif this.tag == 9:
            return OntologyAnnotation.create(to_string(this))

        elif this.tag == 10:
            return OntologyAnnotation.create(to_string(this))

        elif this.tag == 11:
            return OntologyAnnotation.create(to_string(this))

        elif this.tag == 12:
            return OntologyAnnotation.create(to_string(this))

        elif this.tag == 13:
            return OntologyAnnotation.create(to_string(this))

        else: 
            return this.fields[0]


    @staticmethod
    def OfHeaderString(str_1: str) -> CompositeHeader:
        match_value: str = str_1.strip()
        active_pattern_result: Any | None = ActivePatterns__007CRegex_007C__007C(Pattern_InputPattern, match_value)
        if active_pattern_result is not None:
            r: Any = active_pattern_result
            iotype: str = get_item(groups(r), "iotype") or ""
            return CompositeHeader(11, IOType.of_string(iotype))

        else: 
            active_pattern_result_1: Any | None = ActivePatterns__007CRegex_007C__007C(Pattern_OutputPattern, match_value)
            if active_pattern_result_1 is not None:
                r_1: Any = active_pattern_result_1
                iotype_1: str = get_item(groups(r_1), "iotype") or ""
                return CompositeHeader(12, IOType.of_string(iotype_1))

            else: 
                active_pattern_result_2: dict[str, Any] | None = ActivePatterns__007CTermColumn_007C__007C(match_value)
                if active_pattern_result_2 is not None:
                    r_2: dict[str, Any] = active_pattern_result_2
                    match_value_1: str = r_2["TermColumnType"]
                    (pattern_matching_result,) = (None,)
                    if match_value_1 == "Parameter":
                        pattern_matching_result = 0

                    elif match_value_1 == "Parameter Value":
                        pattern_matching_result = 0

                    elif match_value_1 == "Factor":
                        pattern_matching_result = 1

                    elif match_value_1 == "Factor Value":
                        pattern_matching_result = 1

                    elif match_value_1 == "Characteristic":
                        pattern_matching_result = 2

                    elif match_value_1 == "Characteristics":
                        pattern_matching_result = 2

                    elif match_value_1 == "Characteristics Value":
                        pattern_matching_result = 2

                    elif match_value_1 == "Component":
                        pattern_matching_result = 3

                    else: 
                        pattern_matching_result = 4

                    if pattern_matching_result == 0:
                        return CompositeHeader(3, OntologyAnnotation.create(r_2["TermName"]))

                    elif pattern_matching_result == 1:
                        return CompositeHeader(2, OntologyAnnotation.create(r_2["TermName"]))

                    elif pattern_matching_result == 2:
                        return CompositeHeader(1, OntologyAnnotation.create(r_2["TermName"]))

                    elif pattern_matching_result == 3:
                        return CompositeHeader(0, OntologyAnnotation.create(r_2["TermName"]))

                    elif pattern_matching_result == 4:
                        return CompositeHeader(13, str_1)


                else: 
                    return CompositeHeader(10) if (match_value == "Date") else (CompositeHeader(9) if (match_value == "Performer") else (CompositeHeader(5) if (match_value == "Protocol Description") else (CompositeHeader(6) if (match_value == "Protocol Uri") else (CompositeHeader(7) if (match_value == "Protocol Version") else (CompositeHeader(4) if (match_value == "Protocol Type") else (CompositeHeader(8) if (match_value == "Protocol REF") else CompositeHeader(13, match_value)))))))




    @property
    def IsDeprecated(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        (pattern_matching_result,) = (None,)
        if this.tag == 13:
            if this.fields[0].lower() == "sample name":
                pattern_matching_result = 0

            elif this.fields[0].lower() == "source name":
                pattern_matching_result = 1

            elif this.fields[0].lower() == "data file name":
                pattern_matching_result = 2

            elif this.fields[0].lower() == "derived data file":
                pattern_matching_result = 3

            else: 
                pattern_matching_result = 4


        else: 
            pattern_matching_result = 4

        if pattern_matching_result == 0:
            return True

        elif pattern_matching_result == 1:
            return True

        elif pattern_matching_result == 2:
            return True

        elif pattern_matching_result == 3:
            return True

        elif pattern_matching_result == 4:
            return False


    @property
    def IsCvParamColumn(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        if (((this.tag == 3) or (this.tag == 2)) or (this.tag == 1)) or (this.tag == 0):
            return True

        else: 
            return False


    @property
    def IsTermColumn(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        if ((((this.tag == 3) or (this.tag == 2)) or (this.tag == 1)) or (this.tag == 0)) or (this.tag == 4):
            return True

        else: 
            return False


    @property
    def IsFeaturedColumn(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 4) else False

    @property
    def GetFeaturedColumnAccession(self, __unit: None=None) -> str:
        this: CompositeHeader = self
        if this.tag == 4:
            return "DPBO:1000161"

        else: 
            raise Exception(("Tried matching " + str(this)) + " in getFeaturedColumnAccession, but is not a featured column.")


    @property
    def GetColumnAccessionShort(self, __unit: None=None) -> str:
        this: CompositeHeader = self
        if this.tag == 4:
            return this.GetFeaturedColumnAccession

        elif this.tag == 3:
            return this.fields[0].TermAccessionShort

        elif this.tag == 2:
            return this.fields[0].TermAccessionShort

        elif this.tag == 1:
            return this.fields[0].TermAccessionShort

        elif this.tag == 0:
            return this.fields[0].TermAccessionShort

        else: 
            raise Exception(("Tried matching " + str(this)) + ", but is not a column with an accession.")


    @property
    def IsSingleColumn(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        if ((((((((this.tag == 13) or (this.tag == 11)) or (this.tag == 12)) or (this.tag == 8)) or (this.tag == 5)) or (this.tag == 6)) or (this.tag == 7)) or (this.tag == 9)) or (this.tag == 10):
            return True

        else: 
            return False


    @property
    def IsIOType(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        if this.tag == 11:
            return True

        elif this.tag == 12:
            return True

        else: 
            return False


    @property
    def is_input(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 11) else False

    @property
    def is_output(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 12) else False

    @property
    def is_parameter(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 3) else False

    @property
    def is_factor(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 2) else False

    @property
    def is_characteristic(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 1) else False

    @property
    def is_component(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 0) else False

    @property
    def is_protocol_type(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 4) else False

    @property
    def is_protocol_ref(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 8) else False

    @property
    def is_protocol_description(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 5) else False

    @property
    def is_protocol_uri(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 6) else False

    @property
    def is_protocol_version(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 7) else False

    @property
    def is_protocol_column(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        if ((((this.tag == 8) or (this.tag == 5)) or (this.tag == 6)) or (this.tag == 7)) or (this.tag == 4):
            return True

        else: 
            return False


    @property
    def is_performer(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 9) else False

    @property
    def is_date(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 10) else False

    @property
    def is_free_text(self, __unit: None=None) -> bool:
        this: CompositeHeader = self
        return True if (this.tag == 13) else False

    def TryInput(self, __unit: None=None) -> IOType | None:
        this: CompositeHeader = self
        return this.fields[0] if (this.tag == 11) else None

    def TryOutput(self, __unit: None=None) -> IOType | None:
        this: CompositeHeader = self
        return this.fields[0] if (this.tag == 12) else None

    def TryIOType(self, __unit: None=None) -> IOType | None:
        this: CompositeHeader = self
        (pattern_matching_result, io) = (None, None)
        if this.tag == 12:
            pattern_matching_result = 0
            io = this.fields[0]

        elif this.tag == 11:
            pattern_matching_result = 0
            io = this.fields[0]

        else: 
            pattern_matching_result = 1

        if pattern_matching_result == 0:
            return io

        elif pattern_matching_result == 1:
            return None


    def GetUITooltip(self, __unit: None=None) -> str:
        this: CompositeHeader = self
        return CompositeHeader.get_uitooltip(this)

    @staticmethod
    def get_uitooltip(header: Any) -> str:
        (pattern_matching_result,) = (None,)
        if str(type(header)) == "<class \'str\'>":
            if equals(header, "Component"):
                pattern_matching_result = 0

            elif equals(header, "Characteristic"):
                pattern_matching_result = 1

            elif equals(header, "Factor"):
                pattern_matching_result = 2

            elif equals(header, "Parameter"):
                pattern_matching_result = 3

            elif equals(header, "ProtocolType"):
                pattern_matching_result = 4

            elif equals(header, "ProtocolDescription"):
                pattern_matching_result = 5

            elif equals(header, "ProtocolUri"):
                pattern_matching_result = 6

            elif equals(header, "ProtocolVersion"):
                pattern_matching_result = 7

            elif equals(header, "ProtocolREF"):
                pattern_matching_result = 8

            elif equals(header, "Performer"):
                pattern_matching_result = 9

            elif equals(header, "Date"):
                pattern_matching_result = 10

            elif equals(header, "Input"):
                pattern_matching_result = 11

            elif equals(header, "Output"):
                pattern_matching_result = 12

            elif equals(header, "FreeText"):
                pattern_matching_result = 13

            else: 
                pattern_matching_result = 14


        elif header.tag == 1:
            pattern_matching_result = 1

        elif header.tag == 2:
            pattern_matching_result = 2

        elif header.tag == 3:
            pattern_matching_result = 3

        elif header.tag == 4:
            pattern_matching_result = 4

        elif header.tag == 5:
            pattern_matching_result = 5

        elif header.tag == 6:
            pattern_matching_result = 6

        elif header.tag == 7:
            pattern_matching_result = 7

        elif header.tag == 8:
            pattern_matching_result = 8

        elif header.tag == 9:
            pattern_matching_result = 9

        elif header.tag == 10:
            pattern_matching_result = 10

        elif header.tag == 11:
            pattern_matching_result = 11

        elif header.tag == 12:
            pattern_matching_result = 12

        elif header.tag == 13:
            pattern_matching_result = 13

        else: 
            pattern_matching_result = 0

        if pattern_matching_result == 0:
            return "Component columns are used to describe physical components of a experiment, e.g. instrument names, software names, and reagents names."

        elif pattern_matching_result == 1:
            return "Characteristic columns are used for study descriptions and describe inherent properties of the source material, e.g. a certain strain or organism part."

        elif pattern_matching_result == 2:
            return "Use Factor columns to describe independent variables that result in a specific output of your experiment, e.g. the light intensity under which an organism was grown."

        elif pattern_matching_result == 3:
            return "Parameter columns describe steps in your experimental workflow, e.g. the centrifugation time or the temperature used for your assay."

        elif pattern_matching_result == 4:
            return "Defines the protocol type according to your preferred endpoint repository."

        elif pattern_matching_result == 5:
            return "Describe the protocol in free text."

        elif pattern_matching_result == 6:
            return "Web or local address where the in-depth protocol is stored."

        elif pattern_matching_result == 7:
            return "Defines the protocol version."

        elif pattern_matching_result == 8:
            return "Defines the protocol name."

        elif pattern_matching_result == 9:
            return "Defines the protocol performer."

        elif pattern_matching_result == 10:
            return "Defines the date the protocol was performed."

        elif pattern_matching_result == 11:
            return "Only one input column per table. E.g. experimental samples or files."

        elif pattern_matching_result == 12:
            return "Only one output column per table. E.g. experimental samples or files."

        elif pattern_matching_result == 13:
            return "Placeholder"

        elif pattern_matching_result == 14:
            raise Exception(("Unable to parse combination to existing CompositeHeader: `" + str(header)) + "`")


    @staticmethod
    def component(oa: OntologyAnnotation) -> CompositeHeader:
        return CompositeHeader(0, oa)

    @staticmethod
    def characteristic(oa: OntologyAnnotation) -> CompositeHeader:
        return CompositeHeader(1, oa)

    @staticmethod
    def factor(oa: OntologyAnnotation) -> CompositeHeader:
        return CompositeHeader(2, oa)

    @staticmethod
    def parameter(oa: OntologyAnnotation) -> CompositeHeader:
        return CompositeHeader(3, oa)

    @staticmethod
    def protocol_type(__unit: None=None) -> CompositeHeader:
        return CompositeHeader(4)

    @staticmethod
    def protocol_description(__unit: None=None) -> CompositeHeader:
        return CompositeHeader(5)

    @staticmethod
    def protocol_uri(__unit: None=None) -> CompositeHeader:
        return CompositeHeader(6)

    @staticmethod
    def protocol_version(__unit: None=None) -> CompositeHeader:
        return CompositeHeader(7)

    @staticmethod
    def protocol_ref(__unit: None=None) -> CompositeHeader:
        return CompositeHeader(8)

    @staticmethod
    def performer(__unit: None=None) -> CompositeHeader:
        return CompositeHeader(9)

    @staticmethod
    def date(__unit: None=None) -> CompositeHeader:
        return CompositeHeader(10)

    @staticmethod
    def input(io: IOType) -> CompositeHeader:
        return CompositeHeader(11, io)

    @staticmethod
    def output(io: IOType) -> CompositeHeader:
        return CompositeHeader(12, io)

    @staticmethod
    def free_text(s: str) -> CompositeHeader:
        return CompositeHeader(13, s)


CompositeHeader_reflection = _expr387

__all__ = ["IOType_reflection", "CompositeHeader_reflection"]

