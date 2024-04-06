from __future__ import annotations
from abc import abstractmethod
from typing import (Protocol, Generic, TypeVar)
from ..ontology_annotation import OntologyAnnotation
from .value import Value

_PROPERTYVALUE = TypeVar("_PROPERTYVALUE")

class IPropertyValue_1(Protocol, Generic[_PROPERTYVALUE]):
    @abstractmethod
    def GetAdditionalType(self) -> str:
        ...

    @abstractmethod
    def GetCategory(self) -> OntologyAnnotation | None:
        ...

    @abstractmethod
    def GetUnit(self) -> OntologyAnnotation | None:
        ...

    @abstractmethod
    def GetValue(self) -> Value | None:
        ...


