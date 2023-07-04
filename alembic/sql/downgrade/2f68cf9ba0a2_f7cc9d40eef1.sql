DROP TABLE atlas_region_paradigm_class;

DROP TABLE atlas_region_link;

DROP TABLE atlas_region_behavioral_domain;

DROP TABLE atlas_region;

DROP TABLE atlas_paradigm_class;

DROP TABLE atlas_behavioral_domain;

DROP TABLE atlas;

UPDATE alembic_version
SET version_num='2f68cf9ba0a2'
WHERE alembic_version.version_num = 'f7cc9d40eef1';
