from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Kind = Literal["book", "equipment"]


class ItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    kind: Kind


class Item(BaseModel):
    id: int
    title: str
    kind: Kind
    owner_email: str
    available: bool
    created_at: datetime


class LoanCreate(BaseModel):
    item_id: int
    days: int = Field(default=14, ge=1, le=60)


class LoanExtend(BaseModel):
    days: int = Field(ge=1, le=30)


class Loan(BaseModel):
    id: int
    item_id: int
    borrower_email: str
    borrowed_at: datetime
    due_at: datetime
    returned_at: datetime | None
    late_fee_cents: int | None
