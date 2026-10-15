from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import db
from ..auth import current_email
from ..models import Item, ItemCreate

router = APIRouter(prefix="/items", tags=["items"])

_SELECT = """
    SELECT i.id, i.title, i.kind, i.owner_email, i.created_at,
           NOT EXISTS (
               SELECT 1 FROM loans l WHERE l.item_id = i.id AND l.returned_at IS NULL
           ) AS available
    FROM items i
"""


@router.get("", response_model=list[Item])
def list_items(
    _: Annotated[str, Depends(current_email)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[dict]:
    return db.fetch_all(_SELECT + " ORDER BY i.id LIMIT %s OFFSET %s", (limit, offset))


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int, _: Annotated[str, Depends(current_email)]) -> dict:
    item = db.fetch_one(_SELECT + " WHERE i.id = %s", (item_id,))
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("", response_model=Item, status_code=201)
def create_item(body: ItemCreate, email: Annotated[str, Depends(current_email)]) -> dict:
    with db.transaction() as cur:
        cur.execute(
            "INSERT INTO items (title, kind, owner_email) VALUES (%s, %s, %s)"
            " RETURNING id, title, kind, owner_email, created_at, true AS available",
            (body.title, body.kind, email),
        )
        return cur.fetchone()
