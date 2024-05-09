-- Running upgrade e7b61a5dfc8e -> 1ffdc2cfbf96

ALTER TABLE dataset ADD COLUMN source TEXT COMMENT '数据来源';

ALTER TABLE dataset ADD COLUMN download_started_date DATE COMMENT '开始获取的日期';

ALTER TABLE dataset ADD COLUMN planed_finish_date DATE COMMENT '计划完成日期';

ALTER TABLE dataset ADD COLUMN contactor TEXT COMMENT '联系人';

ALTER TABLE dataset ADD COLUMN is_public BOOL COMMENT '是否公开';

ALTER TABLE dataset ADD COLUMN other_species TEXT COMMENT '其他物种名称';

ALTER TABLE dataset ADD COLUMN title TEXT COMMENT '数据集名称';

ALTER TABLE dataset DROP COLUMN start_acquisition_time;

ALTER TABLE dataset DROP COLUMN planed_acquisition_time;

UPDATE alembic_version SET version_num='1ffdc2cfbf96' WHERE alembic_version.version_num = 'e7b61a5dfc8e';

