ALTER TABLE atlas_region
    ADD COLUMN label VARCHAR(255) COMMENT '标签';

UPDATE alembic_version
SET version_num='8dc0f8fefc93'
WHERE alembic_version.version_num = '486b19e5124b';
