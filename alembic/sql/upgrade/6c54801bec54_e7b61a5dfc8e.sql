-- Running upgrade 6c54801bec54 -> e7b61a5dfc8e

ALTER TABLE dataset ADD COLUMN start_acquisition_time DATE COMMENT '开始获取的日期';

ALTER TABLE dataset ADD COLUMN planed_acquisition_time DATE COMMENT '计划完成日期';

ALTER TABLE dataset DROP COLUMN file_acquired_size_gb;

ALTER TABLE eeg_data MODIFY data_update_year DATE NOT NULL COMMENT '数据上传时间';

UPDATE alembic_version SET version_num='e7b61a5dfc8e' WHERE alembic_version.version_num = '6c54801bec54';

