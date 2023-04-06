DROP INDEX ix_file_paradigm_id ON file;

DROP INDEX ix_file_experiment_id ON file;

DROP TABLE file;

DROP TABLE paradigm;

DROP TABLE experiment_human_subject;

DROP TABLE experiment_device;

DROP TABLE experiment_assistant;

DROP INDEX ix_notification_receiver ON notification;

DROP INDEX ix_notification_gmt_create ON notification;

DROP TABLE notification;

DROP INDEX ix_human_subject_user_id ON human_subject;

DROP TABLE human_subject;

DROP INDEX ix_experiment_start_at ON experiment;

DROP TABLE experiment;

DROP INDEX ix_user_username ON user;

DROP INDEX ix_user_staff_id ON user;

DROP TABLE user;

DROP TABLE human_subject_index;

DROP TABLE device;

DROP TABLE alembic_version;
