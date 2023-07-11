ALTER TABLE atlas_paradigm_class
    ADD COLUMN parent_id INTEGER COMMENT '父节点ID，null表示第一层节点';

ALTER TABLE atlas_paradigm_class
    MODIFY description TEXT NOT NULL COMMENT '描述';

ALTER TABLE virtual_file
    MODIFY size FLOAT NOT NULL COMMENT '显示给用户看的文件大小';

UPDATE alembic_version
SET version_num='486b19e5124b'
WHERE alembic_version.version_num = 'f7cc9d40eef1';

