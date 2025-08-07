CREATE TABLE dimproduct (
    productid BIGINT PRIMARY KEY,
    producttype TEXT
);

CREATE TABLE dimdate (
    dateid BIGINT PRIMARY KEY,
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
    segmentid BIGINT PRIMARY KEY,
    city TEXT
);

CREATE TABLE factsales (
    salesid TEXT PRIMARY KEY,
    dateid BIGINT,
    productid BIGINT,
    segmentid BIGINT,
    price_perunit DOUBLE PRECISION,
    quantitysold BIGINT,
    FOREIGN KEY (dateid) REFERENCES dimdate(dateid),
    FOREIGN KEY (productid) REFERENCES dimproduct(productid),
    FOREIGN KEY (segmentid) REFERENCES dimcustomersegment(segmentid)
);

CREATE TABLE stg_dimcustomersegment (
    segmentid BIGINT,
    city TEXT,
    state TEXT,
    PRIMARY KEY (segmentid)
);

CREATE TABLE stg_dimproduct (
    productid BIGINT,
    producttype TEXT,
    state TEXT,
    PRIMARY KEY (productid)
);

CREATE TABLE stg_log (
    last_load timestamptz,
    table_name VARCHAR,
    last_id VARCHAR,
    PRIMARY KEY (table_name)
);

INSERT INTO stg_log (last_load, table_name, last_id) VALUES (NULL, 'dimcustomersegment', NULL);
INSERT INTO stg_log (last_load, table_name, last_id) VALUES (NULL, 'dimdate', NULL);
INSERT INTO stg_log (last_load, table_name, last_id) VALUES (NULL, 'dimproduct', NULL);
INSERT INTO stg_log (last_load, table_name, last_id) VALUES (NULL, 'factsales', NULL);

