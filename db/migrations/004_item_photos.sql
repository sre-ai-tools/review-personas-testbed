-- migrate:up
-- A nullable column with no default only changes the catalog, so the lock is brief.
-- Fail fast instead of queueing behind a long transaction.
SET lock_timeout = '5s';
ALTER TABLE items ADD COLUMN photo_key text;

-- migrate:down
ALTER TABLE items DROP COLUMN photo_key;
