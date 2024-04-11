-- Running downgrade 22e421a98a7c -> 9338b137ec12

ALTER TABLE species DROP INDEX uq_species_latin_name;

ALTER TABLE species MODIFY latin_name TEXT NOT NULL COMMENT '拉丁文名称';

UPDATE alembic_version SET version_num='9338b137ec12' WHERE alembic_version.version_num = '22e421a98a7c';

