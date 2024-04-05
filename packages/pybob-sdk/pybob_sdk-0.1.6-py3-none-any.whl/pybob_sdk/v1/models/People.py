from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional


class FilterOperators(str, Enum):
    equals = "equals"


class FilterModel(BaseModel):
    fieldPath: str
    operator: FilterOperators
    values: List[str]


class HumanReadableValues(str, Enum):
    append = "append"
    replace = "replace"


class SearchModel(BaseModel):
    fields: Optional[List[str]] = None
    filters: Optional[List[FilterModel]] = None
    showInactive: Optional[bool] = None
    humanReadable: Optional[HumanReadableValues] = None


class TerminationReasonUnit(str, Enum):
    days = "days"
    weeks = "weeks"
    months = "months"
    years = "years"


class TerminationReasonType(BaseModel):
    unit: Optional[TerminationReasonUnit] = None
    length: Optional[int] = None
