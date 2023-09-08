DROP TABLE task_step;

DROP TABLE task;

ALTER TABLE atlas_region
    MODIFY label VARCHAR(255) NULL COMMENT '标签';

UPDATE alembic_version
SET version_num='cd57a7609a89'
WHERE alembic_version.version_num = '8dc0f8fefc93';

