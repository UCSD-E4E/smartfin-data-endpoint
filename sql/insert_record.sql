INSERT INTO records (
    published_at,
    event,
    data,
    coreid,
    fw_version
)
VALUES (
    %(published_at)s,
    %(event)s,
    %(data)s,
    %(coreid)s,
    %(fw_version)s
);