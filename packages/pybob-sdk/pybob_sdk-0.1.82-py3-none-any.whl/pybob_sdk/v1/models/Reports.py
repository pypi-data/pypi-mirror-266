from pydantic import BaseModel
from enum import Enum


class ReportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    XLSX = "xlsx"
