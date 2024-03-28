-- Running upgrade 134d9c7fb6e0 -> f8c2dd179c39

ALTER TABLE eegdata_file ADD COLUMN eegdata_id INTEGER NOT NULL COMMENT '脑电数据id';

DROP INDEX ix_eegdata_file_dataset_id ON eegdata_file;

CREATE INDEX ix_eegdata_file_eegdata_id ON eegdata_file (eegdata_id);

ALTER TABLE eegdata_file DROP FOREIGN KEY eegdata_file_ibfk_1;

ALTER TABLE eegdata_file ADD FOREIGN KEY(eegdata_id) REFERENCES eegdata (id);

ALTER TABLE eegdata_file DROP COLUMN dataset_id;

UPDATE alembic_version SET version_num='f8c2dd179c39' WHERE alembic_version.version_num = '134d9c7fb6e0';

