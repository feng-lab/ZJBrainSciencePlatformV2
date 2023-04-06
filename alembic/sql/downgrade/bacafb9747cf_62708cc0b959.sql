DROP TABLE task_step;

DROP TABLE task;

UPDATE alembic_version
SET version_num='62708cc0b959'
WHERE alembic_version.version_num = 'bacafb9747cf';
