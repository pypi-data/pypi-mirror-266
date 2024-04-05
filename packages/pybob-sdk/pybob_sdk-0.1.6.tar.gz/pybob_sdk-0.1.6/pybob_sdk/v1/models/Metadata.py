from pydantic import BaseModel
from enum import Enum
from typing import Optional


class FieldType(str, Enum):
    TEXT = "text"
    TEXT_AREA = "text-area"
    NUMBER = "number"
    DATE = "date"
    LIST = "list"
    MULTI_LIST = "multi-list"
    HIERARCHY_LIST = "hierarchy-list"
    CURRENCY = "currency"
    EMPLOYEE_REFERENCE = "employee-reference"
    DOCUMENT = "document"


class BobField(BaseModel):
    name: str
    category: str
    type: FieldType
    description: Optional[str] = None
    historical: Optional[str] = None
