-- Running downgrade 6c54801bec54 -> fc790ff29f0a

DROP TABLE species;

UPDATE alembic_version SET version_num='fc790ff29f0a' WHERE alembic_version.version_num = '6c54801bec54';

