-- Running upgrade 134d9c7fb6e0 -> 19f8815b6a7b

DROP INDEX ix_eegdata_file_dataset_id ON eegdata_file;

DROP TABLE eegdata_file;

ALTER TABLE eegdata COMMENT '脑电数据';

UPDATE alembic_version SET version_num='19f8815b6a7b' WHERE alembic_version.version_num = '134d9c7fb6e0';

