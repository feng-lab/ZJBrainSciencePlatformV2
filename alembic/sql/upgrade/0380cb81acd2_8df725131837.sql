-- Running upgrade 0380cb81acd2 -> 8df725131837

DROP INDEX ix_eegdata_file_eegdata_id ON eegdata_file;

DROP TABLE eegdata_file;

UPDATE alembic_version SET version_num='8df725131837' WHERE alembic_version.version_num = '0380cb81acd2';

