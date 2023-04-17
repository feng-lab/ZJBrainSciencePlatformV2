SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE storage_file;
DROP TABLE virtual_file;

SET FOREIGN_KEY_CHECKS = 1;

UPDATE alembic_version
SET version_num='01b5380e17fc'
WHERE alembic_version.version_num = '5a840b6cfdfb';

