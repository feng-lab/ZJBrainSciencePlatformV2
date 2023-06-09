-- Running downgrade 01b5380e17fc -> 

DROP TABLE experiment_tag;

DROP TABLE task_step;

DROP TABLE task;

DROP TABLE file;

DROP TABLE paradigm;

DROP TABLE experiment_human_subject;

DROP TABLE experiment_device;

DROP TABLE experiment_assistant;

DROP TABLE notification;

DROP TABLE human_subject;

DROP TABLE experiment;

DROP TABLE user;

DROP TABLE human_subject_index;

DROP TABLE device;

DELETE FROM alembic_version WHERE alembic_version.version_num = '01b5380e17fc';

DROP TABLE alembic_version;

