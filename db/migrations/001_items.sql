-- migrate:up
CREATE TABLE items (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title       text        NOT NULL CHECK (length(title) BETWEEN 1 AND 200),
    kind        text        NOT NULL CHECK (kind IN ('book', 'equipment')),
    owner_email text        NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX items_owner_email_idx ON items (owner_email);

-- migrate:down
DROP TABLE items;
