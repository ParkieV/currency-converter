from datetime import date
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CustomBaseModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)


class CurrencyDTO(CustomBaseModel):
    site: str
    cdr_id: str | None
    nominal: int
    name: str
    char_code: str
    value: float
    unit_value: float
    data_check: date = Field(default_factory=date.today)


class CurrencyDynamicPoint(BaseModel):
    nominal: int
    value: float
    unit_value: float
    date_check: date


class CurrencyDinamicDTO(BaseModel):
    name: str
    char_code: str
    cdr_id: str | None
    dynamics: list[CurrencyDynamicPoint]
