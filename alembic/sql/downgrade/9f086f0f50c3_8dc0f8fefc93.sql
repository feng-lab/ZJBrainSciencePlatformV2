-- Running downgrade 9f086f0f50c3 -> 8dc0f8fefc93

DROP INDEX `ix_DatasetFile_dataset_id` ON `DatasetFile`;

DROP TABLE `DatasetFile`;

DROP INDEX `ix_Dataset_user_id` ON `Dataset`;

DROP TABLE `Dataset`;

UPDATE alembic_version SET version_num='8dc0f8fefc93' WHERE alembic_version.version_num = '9f086f0f50c3';

