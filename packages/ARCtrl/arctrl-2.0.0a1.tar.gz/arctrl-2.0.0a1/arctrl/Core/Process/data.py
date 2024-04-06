from __future__ import annotations
from dataclasses import dataclass
from ...fable_modules.fable_library.list import FSharpList
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.reflection import (TypeInfo, string_type, option_type, list_type, record_type)
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.fable_library.types import (to_string, Record)
from ..comment import (Comment, Comment_reflection)
from .data_file import (DataFile, DataFile__get_AsString, DataFile_reflection)

def _expr326() -> TypeInfo:
    return record_type("ARCtrl.Process.Data", [], Data, lambda: [("ID", option_type(string_type)), ("Name", option_type(string_type)), ("DataType", option_type(DataFile_reflection())), ("Comments", option_type(list_type(Comment_reflection())))])


@dataclass(eq = False, repr = False, slots = True)
class Data(Record):
    ID: str | None
    Name: str | None
    DataType: DataFile | None
    Comments: FSharpList[Comment] | None
    def Print(self, __unit: None=None) -> str:
        this: Data = self
        return to_string(this)

    def PrintCompact(self, __unit: None=None) -> str:
        this: Data = self
        match_value: DataFile | None = this.DataType
        if match_value is None:
            arg_2: str = Data__get_NameAsString(this)
            return to_text(printf("%s"))(arg_2)

        else: 
            t: DataFile = match_value
            arg: str = Data__get_NameAsString(this)
            arg_1: str = DataFile__get_AsString(t)
            return to_text(printf("%s [%s]"))(arg)(arg_1)



Data_reflection = _expr326

def Data_make(id: str | None=None, name: str | None=None, data_type: DataFile | None=None, comments: FSharpList[Comment] | None=None) -> Data:
    return Data(id, name, data_type, comments)


def Data_create_Z2AF98BBE(Id: str | None=None, Name: str | None=None, DataType: DataFile | None=None, Comments: FSharpList[Comment] | None=None) -> Data:
    return Data_make(Id, Name, DataType, Comments)


def Data_get_empty(__unit: None=None) -> Data:
    return Data_create_Z2AF98BBE()


def Data__get_NameAsString(this: Data) -> str:
    return default_arg(this.Name, "")


__all__ = ["Data_reflection", "Data_make", "Data_create_Z2AF98BBE", "Data_get_empty", "Data__get_NameAsString"]

