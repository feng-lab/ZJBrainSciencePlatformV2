-- Running downgrade 0380cb81acd2 -> 46b22297d54e

DROP INDEX ix_eegdata_file_eegdata_id ON eegdata_file;

DROP TABLE eegdata_file;

UPDATE alembic_version SET version_num='46b22297d54e' WHERE alembic_version.version_num = '0380cb81acd2';

