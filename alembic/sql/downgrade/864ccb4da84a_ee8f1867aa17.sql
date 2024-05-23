-- Running downgrade 864ccb4da84a -> ee8f1867aa17

DROP TABLE cumulative_data_per_month;

UPDATE alembic_version SET version_num='ee8f1867aa17' WHERE alembic_version.version_num = '864ccb4da84a';

