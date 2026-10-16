-- migrate:up transaction:false
-- items already holds production data, so build the index without blocking writes.
CREATE INDEX CONCURRENTLY items_kind_created_at_idx ON items (kind, created_at);

-- migrate:down transaction:false
DROP INDEX CONCURRENTLY IF EXISTS items_kind_created_at_idx;
