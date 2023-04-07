ALTER TABLE human_subject
    DROP COLUMN name;

UPDATE alembic_version
SET version_num='ac5d82217032'
WHERE alembic_version.version_num = '01b5380e17fc';

