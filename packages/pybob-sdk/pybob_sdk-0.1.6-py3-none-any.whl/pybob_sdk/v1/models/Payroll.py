from pydantic import BaseModel
from enum import Enum


class PayPeriod(str, Enum):
    Annual = "Annual"
    Hourly = "Hourly"
    Daily = "Daily"
    Weekly = "Weekly"
    Monthly = "Monthly"


class PayFrequency(str, Enum):
    Weekly = "Weekly"
    Monthly = "Monthly"
    ProRata = "Pro rata"
    EveryTwoWeeks = "Every two weeks"
    TwiceAMonth = "Twice a month"
    EveryFourWeeks = "Every four weeks"


class Base(BaseModel):
    value: float
    currency: str


class ExcercisePrice(BaseModel):
    value: float
    currency: str


class VariablePayPeriod(str, Enum):
    Annual = "Annual"
    HalfYearly = "Half-Yearly"
    Quarterly = "Quarterly"
    Monthly = "Monthly"
