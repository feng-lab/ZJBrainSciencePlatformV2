-- Running downgrade 9338b137ec12 -> fc790ff29f0a

ALTER TABLE eeg_data CHANGE data_update_year data_update_year DATETIME NOT NULL COMMENT '数据上传时间';

DROP TABLE species;

UPDATE alembic_version SET version_num='fc790ff29f0a' WHERE alembic_version.version_num = '9338b137ec12';

