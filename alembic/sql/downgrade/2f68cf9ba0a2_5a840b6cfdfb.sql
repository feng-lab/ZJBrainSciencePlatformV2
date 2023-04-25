CREATE TABLE file
(
    experiment_id INTEGER      NOT NULL COMMENT '实验ID',
    paradigm_id   INTEGER COMMENT '范式ID，null表示不属于范式而属于实验',
    name          VARCHAR(255) NOT NULL COMMENT '逻辑路径',
    extension     VARCHAR(50)  NOT NULL COMMENT '文件扩展名',
    size          FLOAT        NOT NULL COMMENT '同一实验下的文件序号',
    is_original   TINYINT(1)   NOT NULL COMMENT '是否是设备产生的原始文件',
    id            INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create    DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT CURRENT_TIMESTAMP,
    gmt_modified  DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT CURRENT_TIMESTAMP,
    is_deleted    TINYINT(1)   NOT NULL COMMENT '该行是否被删除' DEFAULT '0',
    PRIMARY KEY (id),
    CONSTRAINT file_ibfk_1 FOREIGN KEY (experiment_id) REFERENCES experiment (id),
    CONSTRAINT file_ibfk_2 FOREIGN KEY (paradigm_id) REFERENCES paradigm (id)
) COMMENT ='文件';

CREATE INDEX ix_file_paradigm_id ON file (paradigm_id);

CREATE INDEX ix_file_experiment_id ON file (experiment_id);

ALTER TABLE task_step
    DROP FOREIGN KEY task_step_result_file_id;

ALTER TABLE task_step
    ADD CONSTRAINT task_step_result_file_id_fk FOREIGN KEY (result_file_id) REFERENCES file (id);

ALTER TABLE task
    DROP FOREIGN KEY task_source_file;

ALTER TABLE task
    ADD CONSTRAINT task_ibfk_2 FOREIGN KEY (source_file) REFERENCES file (id);

UPDATE alembic_version
SET version_num='5a840b6cfdfb'
WHERE alembic_version.version_num = '2f68cf9ba0a2';

