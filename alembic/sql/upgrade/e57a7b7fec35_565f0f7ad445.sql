ALTER TABLE experiment
    MODIFY type ENUM ('SSVEP','MI','neuron','other') NOT NULL COMMENT '实验类型';

UPDATE alembic_version
SET version_num='565f0f7ad445'
WHERE alembic_version.version_num = 'e57a7b7fec35';

