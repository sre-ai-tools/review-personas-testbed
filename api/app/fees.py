"""Late fees, in whole cents to avoid float rounding."""

from datetime import datetime

DAILY_LATE_FEE_CENTS = 50
MAX_LATE_FEE_CENTS = 2_000


def late_fee_cents(due_at: datetime, returned_at: datetime) -> int:
    days_late = (returned_at.date() - due_at.date()).days
    if days_late <= 0:
        return 0
    return min(days_late * DAILY_LATE_FEE_CENTS, MAX_LATE_FEE_CENTS)
