-- migrate:up
CREATE TABLE loans (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id        bigint      NOT NULL REFERENCES items (id) ON DELETE RESTRICT,
    borrower_email text        NOT NULL,
    borrowed_at    timestamptz NOT NULL DEFAULT now(),
    due_at         timestamptz NOT NULL,
    returned_at    timestamptz,
    late_fee_cents integer     CHECK (late_fee_cents >= 0),
    CHECK (due_at > borrowed_at)
);

-- At most one open loan per item; the API also checks this, but the database is the backstop.
CREATE UNIQUE INDEX loans_one_open_per_item_idx ON loans (item_id) WHERE returned_at IS NULL;
CREATE INDEX loans_borrower_email_idx ON loans (borrower_email);

-- migrate:down
DROP TABLE loans;
