-- Running downgrade f366667dcc42 -> 8dc0f8fefc93

DROP INDEX `ix_DatasetFile_dataset_id` ON `DatasetFile`;

DROP TABLE `DatasetFile`;

DROP TABLE `Dataset`;

UPDATE alembic_version SET version_num='8dc0f8fefc93' WHERE alembic_version.version_num = 'f366667dcc42';

