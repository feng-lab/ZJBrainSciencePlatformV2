CREATE TABLE virtual_file
(
    id            INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create    DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified  DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted    BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    experiment_id INTEGER      NOT NULL COMMENT '实验ID',
    paradigm_id   INTEGER COMMENT '范式ID，null表示不属于范式而属于实验',
    name          VARCHAR(255) NOT NULL COMMENT '文件名',
    file_type     VARCHAR(50)  NOT NULL COMMENT '文件类型',
    is_original   BOOL         NOT NULL COMMENT '是否是设备产生的原始文件',
    size          FLOAT        NOT NULL COMMENT '所有相关文件的大小之和',
    PRIMARY KEY (id),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id),
    FOREIGN KEY (paradigm_id) REFERENCES paradigm (id)
) COMMENT ='虚拟文件';

CREATE INDEX ix_virtual_file_experiment_id ON virtual_file (experiment_id);

CREATE INDEX ix_virtual_file_paradigm_id ON virtual_file (paradigm_id);

CREATE TABLE storage_file
(
    id              INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create      DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified    DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted      BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    virtual_file_id INTEGER      NOT NULL COMMENT '虚拟文件ID',
    name            VARCHAR(255) NOT NULL COMMENT '文件名',
    size            FLOAT        NOT NULL COMMENT '文件大小',
    storage_path    VARCHAR(255) NOT NULL COMMENT '文件系统存储路径',
    PRIMARY KEY (id),
    FOREIGN KEY (virtual_file_id) REFERENCES virtual_file (id)
) COMMENT ='实际文件';

CREATE INDEX ix_storage_file_virtual_file_id ON storage_file (virtual_file_id);

UPDATE alembic_version
SET version_num='5a840b6cfdfb'
WHERE alembic_version.version_num = '01b5380e17fc';

BEGIN;
INSERT INTO virtual_file (id, gmt_create, gmt_modified, is_deleted, experiment_id, paradigm_id, name, file_type,
                          is_original, size)
SELECT id,
       gmt_create,
       gmt_modified,
       is_deleted,
       experiment_id,
       paradigm_id,
       name,
       extension,
       is_original,
       size
FROM file
WHERE is_deleted = FALSE;
INSERT INTO storage_file (gmt_create, gmt_modified, is_deleted, virtual_file_id, name, size, storage_path)
SELECT gmt_create,
       gmt_modified,
       is_deleted,
       id,
       name,
       size,
       concat(experiment_id, '/', if(extension = '', id, concat(id, '.', extension))) AS storage_path
FROM file
WHERE is_deleted = FALSE;
COMMIT;

