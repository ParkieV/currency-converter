CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE currencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site VARCHAR,
    cdr_id VARCHAR,
    name VARCHAR,
    char_code VARCHAR,
    value NUMERIC,
    nominal INT,
    unit_value NUMERIC,
    data_check DATE
)
