-- Running downgrade 8d47b0117044 -> 864ccb4da84a

ALTER TABLE dataset DROP COLUMN is_cleaned;

ALTER TABLE dataset DROP COLUMN planed_download_per_month;

UPDATE alembic_version SET version_num='864ccb4da84a' WHERE alembic_version.version_num = '8d47b0117044';

