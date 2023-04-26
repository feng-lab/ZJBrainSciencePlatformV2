USE zj_brain_science_platform;

BEGIN;
INSERT INTO file(id,
                 experiment_id,
                 paradigm_id,
                 name,
                 extension,
                 size,
                 is_original,
                 gmt_create,
                 gmt_modified,
                 is_deleted)
SELECT virtual_file.id,
       virtual_file.experiment_id,
       virtual_file.paradigm_id,
       virtual_file.name,
       virtual_file.file_type,
       virtual_file.size,
       virtual_file.is_original,
       virtual_file.gmt_create,
       virtual_file.gmt_modified,
       FALSE
FROM virtual_file
         INNER JOIN storage_file ON virtual_file.id = storage_file.virtual_file_id
WHERE virtual_file.is_deleted = FALSE
  AND storage_file.is_deleted = FALSE
  AND storage_file.name = virtual_file.name;
COMMIT;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE storage_file;
DROP TABLE virtual_file;

SET FOREIGN_KEY_CHECKS = 1;

UPDATE alembic_version
SET version_num='01b5380e17fc'
WHERE alembic_version.version_num = '5a840b6cfdfb';

