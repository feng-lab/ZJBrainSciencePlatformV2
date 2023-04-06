UPDATE experiment
SET type = 'SSVEP'
WHERE type = 'other';

ALTER TABLE experiment
    MODIFY type ENUM ('SSVEP','MI','neuron') NOT NULL COMMENT '实验类型';

UPDATE alembic_version
SET version_num='e57a7b7fec35'
WHERE alembic_version.version_num = '565f0f7ad445';
