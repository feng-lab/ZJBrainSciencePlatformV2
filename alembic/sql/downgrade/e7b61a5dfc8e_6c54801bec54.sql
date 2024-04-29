-- Running downgrade e7b61a5dfc8e -> 6c54801bec54

ALTER TABLE eeg_data CHANGE data_update_year data_update_year DATETIME NOT NULL COMMENT '数据上传时间';

ALTER TABLE dataset ADD COLUMN file_acquired_size_gb FLOAT COMMENT '已获取数据(GB)';

ALTER TABLE dataset DROP COLUMN planed_acquisition_time;

ALTER TABLE dataset DROP COLUMN start_acquisition_time;

UPDATE alembic_version SET version_num='6c54801bec54' WHERE alembic_version.version_num = 'e7b61a5dfc8e';

