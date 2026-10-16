"""Loads demo items into a local or staging database. Never run against production.

    DB_SECRET_ARN=... DB_HOST=... DB_NAME=... python -m app.seed
"""

import json
from pathlib import Path

from . import db

SEED_FILE = Path(__file__).parent / "data" / "seed_items.json"


def main() -> None:
    items = json.loads(SEED_FILE.read_text())
    with db.transaction() as cur:
        cur.executemany(
            "INSERT INTO items (title, kind, owner_email) VALUES (%s, %s, %s)",
            [(i["title"], i["kind"], i["owner_email"]) for i in items],
        )
    print(f"Inserted {len(items)} items")


if __name__ == "__main__":
    main()
