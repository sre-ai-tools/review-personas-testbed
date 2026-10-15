-- migrate:up transaction:false
-- loans already holds production data, so build the index without blocking writes.
-- No IF NOT EXISTS: a failed concurrent build leaves an INVALID index, which must be dropped
-- before retrying rather than silently kept.
CREATE INDEX CONCURRENTLY loans_open_due_at_idx
    ON loans (borrower_email, due_at)
    WHERE returned_at IS NULL;

-- migrate:down transaction:false
DROP INDEX CONCURRENTLY IF EXISTS loans_open_due_at_idx;
