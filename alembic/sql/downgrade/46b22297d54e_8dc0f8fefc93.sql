-- Running downgrade 46b22297d54e -> 8dc0f8fefc93

DROP INDEX ix_dataset_file_dataset_id ON dataset_file;

DROP TABLE dataset_file;

DROP INDEX ix_eegdata_user_id ON eegdata;

DROP TABLE eegdata;

DROP INDEX ix_dataset_user_id ON dataset;

DROP TABLE dataset;

UPDATE alembic_version SET version_num='8dc0f8fefc93' WHERE alembic_version.version_num = '46b22297d54e';

