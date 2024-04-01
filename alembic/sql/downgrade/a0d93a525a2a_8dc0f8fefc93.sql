DROP TABLE dataset_file;

DROP TABLE dataset;

UPDATE alembic_version
SET version_num='8dc0f8fefc93'
WHERE alembic_version.version_num = 'a0d93a525a2a';
