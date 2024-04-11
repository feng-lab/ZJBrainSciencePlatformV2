-- Running upgrade 9338b137ec12 -> 22e421a98a7c

ALTER TABLE species MODIFY latin_name VARCHAR(255) NOT NULL COMMENT '拉丁文名称';

ALTER TABLE species ADD CONSTRAINT uq_species_latin_name UNIQUE (latin_name);

UPDATE alembic_version SET version_num='22e421a98a7c' WHERE alembic_version.version_num = '9338b137ec12';

