-- Running downgrade 8dc0f8fefc93 -> 

DROP TABLE task_step;

DROP TABLE task;

DROP INDEX ix_storage_file_virtual_file_id ON storage_file;

DROP TABLE storage_file;

DROP INDEX ix_virtual_file_paradigm_id ON virtual_file;

DROP INDEX ix_virtual_file_experiment_id ON virtual_file;

DROP TABLE virtual_file;

DROP TABLE paradigm;

DROP TABLE experiment_tag;

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

DROP TABLE atlas_region_paradigm_class;

DROP TABLE atlas_region_link;

DROP TABLE atlas_region_behavioral_domain;

DROP TABLE atlas_region;

DROP TABLE atlas_paradigm_class;

DROP TABLE atlas_behavioral_domain;

DROP TABLE atlas;

DELETE
FROM alembic_version
WHERE alembic_version.version_num = '8dc0f8fefc93';

DROP TABLE alembic_version;

