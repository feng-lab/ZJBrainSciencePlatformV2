-- Running upgrade 864ccb4da84a -> 8d47b0117044

ALTER TABLE dataset ADD COLUMN planed_download_per_month FLOAT COMMENT '每月计划下载量';

ALTER TABLE dataset ADD COLUMN is_cleaned BOOL COMMENT '是否清洗过数据';

UPDATE alembic_version SET version_num='8d47b0117044' WHERE alembic_version.version_num = '864ccb4da84a';

