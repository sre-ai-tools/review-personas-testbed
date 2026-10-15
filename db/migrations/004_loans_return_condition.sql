-- migrate:up
-- Record the condition an item came back in. loans has about 50M rows in production.
ALTER TABLE loans ADD COLUMN returned_condition text NOT NULL;
CREATE INDEX loans_returned_condition_idx ON loans (returned_condition);

-- migrate:down
DROP INDEX loans_returned_condition_idx;
ALTER TABLE loans DROP COLUMN returned_condition;
