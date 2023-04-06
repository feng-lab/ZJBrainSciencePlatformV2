CREATE TABLE task
(
    name         VARCHAR(255)                                             NOT NULL COMMENT '任务名',
    description  TEXT                                                     NOT NULL COMMENT '任务描述',
    source_file  INTEGER                                                  NOT NULL COMMENT '任务分析的文件ID',
    type         ENUM ('preprocess','analysis','preprocess_analysis')     NOT NULL COMMENT '任务类型',
    start_at     DATETIME COMMENT '任务开始执行的时间',
    end_at       DATETIME COMMENT '任务结束时间',
    status       ENUM ('wait_start','running','done','error','cancelled') NOT NULL COMMENT '任务状态',
    creator      INTEGER                                                  NOT NULL COMMENT '任务创建者ID',
    id           INTEGER                                                  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME                                                 NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified DATETIME                                                 NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted   BOOL                                                     NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    PRIMARY KEY (id),
    FOREIGN KEY (creator) REFERENCES user (id),
    FOREIGN KEY (source_file) REFERENCES file (id)
) COMMENT ='任务';

CREATE TABLE task_step
(
    task_id      INTEGER                                                  NOT NULL COMMENT '任务ID',
    name         VARCHAR(255)                                             NOT NULL COMMENT '步骤名字',
    type         ENUM ('preprocess','analysis')                           NOT NULL COMMENT '任务步骤类型',
    parameter    TEXT                                                     NOT NULL COMMENT '步骤参数JSON',
    `index`      INTEGER                                                  NOT NULL COMMENT '任务中的步骤顺序',
    status       ENUM ('wait_start','running','done','error','cancelled') NOT NULL COMMENT '步骤状态',
    start_at     DATETIME COMMENT '步骤开始执行的时间',
    end_at       DATETIME COMMENT '步骤结束时间',
    id           INTEGER                                                  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME                                                 NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified DATETIME                                                 NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted   BOOL                                                     NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    PRIMARY KEY (id),
    FOREIGN KEY (task_id) REFERENCES task (id)
) COMMENT ='任务步骤';

UPDATE alembic_version
SET version_num='bacafb9747cf'
WHERE alembic_version.version_num = '62708cc0b959';

