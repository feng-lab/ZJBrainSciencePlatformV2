ALTER TABLE virtual_file
    MODIFY size FLOAT NOT NULL COMMENT '所有相关文件的大小之和';

ALTER TABLE atlas_paradigm_class
    MODIFY description TEXT NULL COMMENT '描述';

ALTER TABLE atlas_paradigm_class
    DROP COLUMN parent_id;

UPDATE alembic_version
SET version_num='f7cc9d40eef1'
WHERE alembic_version.version_num = '486b19e5124b';

