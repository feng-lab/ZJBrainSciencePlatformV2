ALTER TABLE task
    DROP FOREIGN KEY task_ibfk_2;

ALTER TABLE task
    ADD CONSTRAINT task_source_file FOREIGN KEY (source_file) REFERENCES virtual_file (id);

ALTER TABLE task_step
    DROP FOREIGN KEY task_step_result_file_id_fk;

ALTER TABLE task_step
    ADD CONSTRAINT task_step_result_file_id FOREIGN KEY (result_file_id) REFERENCES virtual_file (id);

DROP TABLE file;

UPDATE alembic_version
SET version_num='2f68cf9ba0a2'
WHERE alembic_version.version_num = '5a840b6cfdfb';

