-- Running downgrade 134d9c7fb6e0 -> a9e5944a8108

ALTER TABLE eegdata COMMENT '数据集';

DROP INDEX ix_eegdata_file_dataset_id ON eegdata_file;

DROP TABLE eegdata_file;

UPDATE alembic_version SET version_num='a9e5944a8108' WHERE alembic_version.version_num = '134d9c7fb6e0';

