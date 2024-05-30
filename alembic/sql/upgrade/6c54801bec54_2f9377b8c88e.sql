-- Running upgrade 6c54801bec54 -> 2f9377b8c88e

CREATE TABLE cumulative_data_per_month (
    date DATE NOT NULL COMMENT '日期', 
    full_data_size FLOAT COMMENT '数据总量(GB)', 
    full_data_count FLOAT COMMENT '数据条目', 
    id INTEGER NOT NULL COMMENT '主键' AUTO_INCREMENT, 
    gmt_create DATETIME NOT NULL COMMENT '创建时间' DEFAULT now(), 
    gmt_modified DATETIME NOT NULL COMMENT '修改时间' DEFAULT now(), 
    is_deleted BOOL NOT NULL COMMENT '该行是否被删除' DEFAULT false, 
    PRIMARY KEY (id)
)COMMENT='数据总量';

ALTER TABLE dataset ADD COLUMN source TEXT COMMENT '数据来源';

ALTER TABLE dataset ADD COLUMN download_started_date DATE COMMENT '开始获取的日期';

ALTER TABLE dataset ADD COLUMN planed_finish_date DATE COMMENT '计划完成日期';

ALTER TABLE dataset ADD COLUMN contactor TEXT COMMENT '联系人';

ALTER TABLE dataset ADD COLUMN is_public BOOL COMMENT '是否公开';

ALTER TABLE dataset ADD COLUMN other_species TEXT COMMENT '其他物种名称';

ALTER TABLE dataset ADD COLUMN title TEXT COMMENT '数据集名称';

ALTER TABLE dataset ADD COLUMN planed_download_per_month FLOAT COMMENT '每月计划下载量';

ALTER TABLE dataset ADD COLUMN is_cleaned BOOL COMMENT '是否清洗过数据';

ALTER TABLE dataset DROP COLUMN file_acquired_size_gb;

ALTER TABLE eeg_data MODIFY data_update_year DATE NOT NULL COMMENT '数据上传时间';

UPDATE alembic_version SET version_num='2f9377b8c88e' WHERE alembic_version.version_num = '6c54801bec54';

