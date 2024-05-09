-- Running downgrade 1ffdc2cfbf96 -> e7b61a5dfc8e

ALTER TABLE dataset ADD COLUMN planed_acquisition_time DATE COMMENT '计划完成日期';

ALTER TABLE dataset ADD COLUMN start_acquisition_time DATE COMMENT '开始获取的日期';

ALTER TABLE dataset DROP COLUMN title;

ALTER TABLE dataset DROP COLUMN other_species;

ALTER TABLE dataset DROP COLUMN is_public;

ALTER TABLE dataset DROP COLUMN contactor;

ALTER TABLE dataset DROP COLUMN planed_finish_date;

ALTER TABLE dataset DROP COLUMN download_started_date;

ALTER TABLE dataset DROP COLUMN source;

UPDATE alembic_version SET version_num='e7b61a5dfc8e' WHERE alembic_version.version_num = '1ffdc2cfbf96';

