ALTER TABLE task_step
    ADD COLUMN result_file_id INTEGER COMMENT '结果文件ID';

ALTER TABLE task_step
    ADD COLUMN error_msg VARCHAR(255) COMMENT '错误信息';

ALTER TABLE task_step
    ADD CONSTRAINT task_step_result_file_id_fk FOREIGN KEY (result_file_id) REFERENCES file (id);

UPDATE alembic_version
SET version_num='e57a7b7fec35'
WHERE alembic_version.version_num = 'bacafb9747cf';

