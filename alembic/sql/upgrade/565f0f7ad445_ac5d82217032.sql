CREATE TABLE experiment_tag
(
    experiment_id INTEGER     NOT NULL COMMENT '实验ID',
    tag           VARCHAR(50) NOT NULL COMMENT '标签',
    PRIMARY KEY (experiment_id, tag),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id)
) COMMENT ='实验标签';

UPDATE alembic_version
SET version_num='ac5d82217032'
WHERE alembic_version.version_num = '565f0f7ad445';
