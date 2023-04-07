ALTER TABLE human_subject
    ADD COLUMN name VARCHAR(50) COMMENT '姓名';

UPDATE alembic_version
SET version_num='01b5380e17fc'
WHERE alembic_version.version_num = 'ac5d82217032';

