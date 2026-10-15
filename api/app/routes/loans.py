from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from .. import db
from ..auth import current_email
from ..fees import late_fee_cents
from ..models import Loan, LoanCreate

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("", response_model=Loan, status_code=201)
def borrow(body: LoanCreate, email: Annotated[str, Depends(current_email)]) -> dict:
    now = datetime.now(UTC)
    with db.transaction() as cur:
        # Lock the item so two people can't borrow it at the same moment.
        cur.execute("SELECT id FROM items WHERE id = %s FOR UPDATE", (body.item_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Item not found")
        cur.execute(
            "SELECT 1 FROM loans WHERE item_id = %s AND returned_at IS NULL", (body.item_id,)
        )
        if cur.fetchone() is not None:
            raise HTTPException(status_code=409, detail="Item is already on loan")
        cur.execute(
            "INSERT INTO loans (item_id, borrower_email, borrowed_at, due_at)"
            " VALUES (%s, %s, %s, %s) RETURNING *",
            (body.item_id, email, now, now + timedelta(days=body.days)),
        )
        return cur.fetchone()


@router.post("/{loan_id}/return", response_model=Loan)
def return_item(loan_id: int, email: Annotated[str, Depends(current_email)]) -> dict:
    now = datetime.now(UTC)
    with db.transaction() as cur:
        cur.execute("SELECT * FROM loans WHERE id = %s FOR UPDATE", (loan_id,))
        loan = cur.fetchone()
        if loan is None:
            raise HTTPException(status_code=404, detail="Loan not found")
        if loan["borrower_email"] != email:
            raise HTTPException(status_code=403, detail="Only the borrower can return this item")
        if loan["returned_at"] is not None:
            raise HTTPException(status_code=409, detail="Already returned")
        cur.execute(
            "UPDATE loans SET returned_at = %s, late_fee_cents = %s WHERE id = %s RETURNING *",
            (now, late_fee_cents(loan["due_at"], now), loan_id),
        )
        return cur.fetchone()


@router.get("/overdue", response_model=list[Loan])
def overdue(email: Annotated[str, Depends(current_email)]) -> list[dict]:
    return db.fetch_all(
        "SELECT * FROM loans WHERE borrower_email = %s AND returned_at IS NULL AND due_at < now()"
        " ORDER BY due_at LIMIT 100",
        (email,),
    )
