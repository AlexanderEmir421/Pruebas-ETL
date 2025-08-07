CREATE TABLE dimproduct (
    productid BIGINT,
    producttype TEXT
);
CREATE TABLE dimdate (
    dateid BIGINT,
    date TEXT,
    year BIGINT,
    quarter BIGINT,
    quartername TEXT,
    month BIGINT,
    monthname TEXT,
    day BIGINT,
    weekday BIGINT,
    weekdayname TEXT
);
CREATE TABLE dimcustomersegment (
    segmentid BIGINT,
    city TEXT
);
CREATE TABLE factsales (
    salesid TEXT,
    dateid BIGINT,
    productid BIGINT,
    segmentid BIGINT,
    price_perunit DOUBLE PRECISION,
    quantitysold BIGINT
);

CREATE TABLE stg_dimcustomersegment (
    segmentid BIGINT,
    city TEXT,
    state TEXT
);

CREATE TABLE stg_log(
    last_load timestamptz,
    table_name varchar,
    last_id varchar
);
