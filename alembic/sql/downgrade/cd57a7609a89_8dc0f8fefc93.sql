ALTER TABLE atlas_region
    MODIFY label VARCHAR(255) NOT NULL COMMENT '标签';

CREATE TABLE task
(
    id           INTEGER                                                  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME                                                 NOT NULL COMMENT '创建时间'       DEFAULT CURRENT_TIMESTAMP,
    gmt_modified DATETIME                                                 NOT NULL COMMENT '修改时间'       DEFAULT CURRENT_TIMESTAMP,
    is_deleted   TINYINT(1)                                               NOT NULL COMMENT '该行是否被删除' DEFAULT '0',
    name         VARCHAR(255)                                             NOT NULL COMMENT '任务名',
    description  TEXT                                                     NOT NULL COMMENT '任务描述',
    source_file  INTEGER                                                  NOT NULL COMMENT '任务分析的文件ID',
    type         ENUM ('preprocess','analysis','preprocess_analysis')     NOT NULL COMMENT '任务类型',
    start_at     DATETIME COMMENT '任务开始执行的时间',
    end_at       DATETIME COMMENT '任务结束时间',
    status       ENUM ('wait_start','running','done','error','cancelled') NOT NULL COMMENT '任务状态',
    creator      INTEGER                                                  NOT NULL COMMENT '任务创建者ID',
    PRIMARY KEY (id),
    CONSTRAINT task_ibfk_1 FOREIGN KEY (creator) REFERENCES user (id),
    CONSTRAINT task_ibfk_2 FOREIGN KEY (source_file) REFERENCES virtual_file (id)
) DEFAULT CHARSET = utf8mb4 COMMENT ='任务'
  ENGINE = InnoDB
  COLLATE utf8mb4_0900_ai_ci;

CREATE TABLE task_step
(
    id             INTEGER                                                  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create     DATETIME                                                 NOT NULL COMMENT '创建时间'       DEFAULT CURRENT_TIMESTAMP,
    gmt_modified   DATETIME                                                 NOT NULL COMMENT '修改时间'       DEFAULT CURRENT_TIMESTAMP,
    is_deleted     TINYINT(1)                                               NOT NULL COMMENT '该行是否被删除' DEFAULT '0',
    task_id        INTEGER                                                  NOT NULL COMMENT '任务ID',
    name           VARCHAR(255)                                             NOT NULL COMMENT '步骤名字',
    type           ENUM ('preprocess','analysis')                           NOT NULL COMMENT '任务步骤类型',
    parameter      TEXT                                                     NOT NULL COMMENT '步骤参数JSON',
    `index`        INTEGER                                                  NOT NULL COMMENT '任务中的步骤顺序',
    status         ENUM ('wait_start','running','done','error','cancelled') NOT NULL COMMENT '步骤状态',
    start_at       DATETIME COMMENT '步骤开始执行的时间',
    end_at         DATETIME COMMENT '步骤结束时间',
    result_file_id INTEGER COMMENT '结果文件ID',
    error_msg      VARCHAR(255) COMMENT '错误信息',
    PRIMARY KEY (id),
    CONSTRAINT task_step_ibfk_2 FOREIGN KEY (result_file_id) REFERENCES virtual_file (id),
    CONSTRAINT task_step_ibfk_1 FOREIGN KEY (task_id) REFERENCES task (id)
) DEFAULT CHARSET = utf8mb4 COMMENT ='任务步骤'
  ENGINE = InnoDB
  COLLATE utf8mb4_0900_ai_ci;

UPDATE alembic_version
SET version_num='8dc0f8fefc93'
WHERE alembic_version.version_num = 'cd57a7609a89';

