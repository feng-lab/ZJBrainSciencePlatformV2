-- Running downgrade a9e5944a8108 -> a0d93a525a2a

DROP INDEX ix_eegdata_user_id ON eegdata;

DROP TABLE eegdata;

UPDATE alembic_version SET version_num='a0d93a525a2a' WHERE alembic_version.version_num = 'a9e5944a8108';

