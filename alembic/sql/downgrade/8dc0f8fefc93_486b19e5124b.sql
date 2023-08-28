ALTER TABLE atlas_region
    DROP COLUMN label;

UPDATE alembic_version
SET version_num='486b19e5124b'
WHERE alembic_version.version_num = '8dc0f8fefc93';

