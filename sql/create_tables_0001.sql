CREATE TABLE version (
    version INTEGER NOT NULL
);

INSERT INTO version (version) VALUES (1);

CREATE TABLE records (
    published_at TIMESTAMPZ NOT NULL,
    event TEXT NOT NULL,
    data TEXT NOT NULL,
    coreid TEXT NOT NULL,
    fw_version INTEGER NOT NULL
    CONSTRAING records_pkey PRIMARY KEY (coreid, published_at, event)
) WITH (
    tsdb.hypertable,
    tsdb.partition_column='published_at',
    tsdb.segmentby='coreid',
    tsdb.orderby='published_at DESC',
    tsdb.chunk_interval='30 days'
)