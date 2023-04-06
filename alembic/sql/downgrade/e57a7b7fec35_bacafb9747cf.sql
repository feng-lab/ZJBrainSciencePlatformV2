ALTER TABLE task_step
    DROP FOREIGN KEY task_step_result_file_id_fk;

ALTER TABLE task_step
    DROP COLUMN error_msg;

ALTER TABLE task_step
    DROP COLUMN result_file_id;

UPDATE alembic_version
SET version_num='bacafb9747cf'
WHERE alembic_version.version_num = 'e57a7b7fec35';
