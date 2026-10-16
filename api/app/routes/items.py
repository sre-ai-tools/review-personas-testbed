from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import db, photos
from ..auth import current_email
from ..models import Item, ItemCreate, PhotoUpload, PhotoUploadRequest

router = APIRouter(prefix="/items", tags=["items"])

_SELECT = """
    SELECT i.id, i.title, i.kind, i.owner_email, i.created_at, i.photo_key,
           NOT EXISTS (
               SELECT 1 FROM loans l WHERE l.item_id = i.id AND l.returned_at IS NULL
           ) AS available
    FROM items i
"""


def _with_photo(row: dict) -> dict:
    key = row.pop("photo_key", None)
    return {**row, "photo_url": photos.download_url(key) if key else None}


@router.get("", response_model=list[Item])
def list_items(
    _: Annotated[str, Depends(current_email)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[dict]:
    rows = db.fetch_all(_SELECT + " ORDER BY i.id LIMIT %s OFFSET %s", (limit, offset))
    return [_with_photo(row) for row in rows]


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int, _: Annotated[str, Depends(current_email)]) -> dict:
    item = db.fetch_one(_SELECT + " WHERE i.id = %s", (item_id,))
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return _with_photo(item)


@router.post("", response_model=Item, status_code=201)
def create_item(body: ItemCreate, email: Annotated[str, Depends(current_email)]) -> dict:
    with db.transaction() as cur:
        cur.execute(
            "INSERT INTO items (title, kind, owner_email) VALUES (%s, %s, %s)"
            " RETURNING id, title, kind, owner_email, created_at, true AS available",
            (body.title, body.kind, email),
        )
        return cur.fetchone()


@router.post("/{item_id}/photo", response_model=PhotoUpload)
def request_photo_upload(
    item_id: int, body: PhotoUploadRequest, email: Annotated[str, Depends(current_email)]
) -> dict:
    key = photos.photo_key(item_id, body.content_type)
    with db.transaction() as cur:
        cur.execute("SELECT owner_email FROM items WHERE id = %s FOR UPDATE", (item_id,))
        item = cur.fetchone()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        if item["owner_email"] != email:
            raise HTTPException(status_code=403, detail="Only the owner can change the photo")
        cur.execute("UPDATE items SET photo_key = %s WHERE id = %s", (key, item_id))
    return photos.upload(key, body.content_type)
