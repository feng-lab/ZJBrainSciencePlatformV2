-- Running downgrade 2f9377b8c88e -> 6c54801bec54

ALTER TABLE eeg_data CHANGE data_update_year data_update_year DATETIME NOT NULL COMMENT '数据上传时间';

ALTER TABLE dataset ADD COLUMN file_acquired_size_gb FLOAT COMMENT '已获取数据(GB)';

ALTER TABLE dataset DROP COLUMN is_cleaned;

ALTER TABLE dataset DROP COLUMN planed_download_per_month;

ALTER TABLE dataset DROP COLUMN title;

ALTER TABLE dataset DROP COLUMN other_species;

ALTER TABLE dataset DROP COLUMN is_public;

ALTER TABLE dataset DROP COLUMN contactor;

ALTER TABLE dataset DROP COLUMN planed_finish_date;

ALTER TABLE dataset DROP COLUMN download_started_date;

ALTER TABLE dataset DROP COLUMN source;

DROP TABLE cumulative_data_per_month;

UPDATE alembic_version SET version_num='6c54801bec54' WHERE alembic_version.version_num = '2f9377b8c88e';

