DROP TABLE `DatasetFile`;
DROP INDEX `ix_DatasetFile_dataset_id` ON `DatasetFile`;

DROP TABLE `Dataset`;
DROP INDEX `ix_Dataset_user_id` ON `Dataset`;

UPDATE alembic_version
SET version_num='8dc0f8fefc93'
WHERE alembic_version.version_num = 'a0d93a525a2a';
