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
    photo_url: str | None = None


class LoanCreate(BaseModel):
    item_id: int
    days: int = Field(default=14, ge=1, le=60)


class Loan(BaseModel):
    id: int
    item_id: int
    borrower_email: str
    borrowed_at: datetime
    due_at: datetime
    returned_at: datetime | None
    late_fee_cents: int | None


class PhotoUploadRequest(BaseModel):
    content_type: Literal["image/jpeg", "image/png", "image/webp"]


class PhotoUpload(BaseModel):
    """A presigned S3 POST: the browser sends `fields` plus the file to `url`."""

    url: str
    fields: dict[str, str]
