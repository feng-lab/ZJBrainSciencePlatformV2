CREATE TABLE alembic_version
(
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 576fba37f0c3

CREATE TABLE user
(
    id               INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create       DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified     DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted       BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    username         VARCHAR(255) NOT NULL COMMENT '用户名',
    hashed_password  VARCHAR(255) NOT NULL COMMENT '密码哈希',
    staff_id         VARCHAR(255) NOT NULL COMMENT '员工号',
    last_login_time  DATETIME COMMENT '上次登录时间',
    last_logout_time DATETIME COMMENT '上次下线时间',
    access_level     INTEGER      NOT NULL COMMENT '权限级别',
    PRIMARY KEY (id)
) COMMENT ='用户';

CREATE UNIQUE INDEX ix_user_username ON user (username);

CREATE TABLE experiment
(
    id               INTEGER                      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create       DATETIME                     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified     DATETIME                     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted       BOOL                         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    name             VARCHAR(255)                 NOT NULL COMMENT '实验名称',
    type             ENUM ('SSVEP','MI','neuron') NOT NULL COMMENT '实验类型',
    description      TEXT                         NOT NULL COMMENT '实验描述',
    location         VARCHAR(255)                 NOT NULL COMMENT '实验地点',
    start_at         DATETIME                     NOT NULL COMMENT '实验开始时间',
    end_at           DATETIME                     NOT NULL COMMENT '实验结束时间',
    main_operator    INTEGER                      NOT NULL COMMENT '主操作者ID',
    is_non_invasive  BOOL COMMENT '是否为无创实验',
    subject_type     VARCHAR(50) COMMENT '被试类型',
    subject_num      INTEGER COMMENT '被试数量',
    neuron_source    VARCHAR(50) COMMENT '神经元细胞来源部位',
    stimulation_type VARCHAR(50) COMMENT '刺激类型',
    session_num      INTEGER COMMENT '实验session数量',
    trail_num        INTEGER COMMENT '实验trail数量',
    is_shared        BOOL COMMENT '实验是否公开',
    PRIMARY KEY (id),
    FOREIGN KEY (main_operator) REFERENCES user (id)
) COMMENT ='实验';

CREATE INDEX ix_experiment_start_at ON experiment (start_at);

CREATE TABLE notification
(
    id           INTEGER                   NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_modified DATETIME                  NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted   BOOL                      NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    gmt_create   DATETIME                  NOT NULL COMMENT '创建时间'       DEFAULT now(),
    type         ENUM ('task_step_status') NOT NULL COMMENT '消息类型',
    creator      INTEGER                   NOT NULL COMMENT '消息发送者ID',
    receiver     INTEGER                   NOT NULL COMMENT '消息接收者ID',
    status       ENUM ('unread','read')    NOT NULL COMMENT '消息状态',
    content      TEXT                      NOT NULL COMMENT '消息内容',
    PRIMARY KEY (id),
    FOREIGN KEY (creator) REFERENCES user (id),
    FOREIGN KEY (receiver) REFERENCES user (id)
) COMMENT ='通知';

CREATE INDEX ix_notification_gmt_create ON notification (gmt_create);

CREATE INDEX ix_notification_receiver ON notification (receiver);

CREATE TABLE experiment_assistant
(
    id            INTEGER  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create    DATETIME NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified  DATETIME NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted    BOOL     NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    user_id       INTEGER  NOT NULL,
    experiment_id INTEGER  NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id),
    FOREIGN KEY (user_id) REFERENCES user (id)
) COMMENT ='实验助手';

CREATE INDEX ix_experiment_assistant_experiment_id ON experiment_assistant (experiment_id);

CREATE TABLE file
(
    id            INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create    DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified  DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted    BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    experiment_id INTEGER      NOT NULL COMMENT '实验ID',
    name          VARCHAR(255) NOT NULL COMMENT '逻辑路径',
    extension     VARCHAR(50)  NOT NULL COMMENT '文件扩展名',
    `index`       INTEGER      NOT NULL COMMENT '同一实验下的文件序号',
    size          FLOAT        NOT NULL COMMENT '同一实验下的文件序号',
    is_original   BOOL         NOT NULL COMMENT '是否是设备产生的原始文件',
    PRIMARY KEY (id),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id)
) COMMENT ='文件';

CREATE INDEX ix_file_experiment_id ON file (experiment_id);

CREATE INDEX ix_file_index ON file (`index`);

CREATE TABLE paradigm
(
    id            INTEGER  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create    DATETIME NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified  DATETIME NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted    BOOL     NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    experiment_id INTEGER  NOT NULL COMMENT '实验ID',
    creator       INTEGER  NOT NULL COMMENT '创建者ID',
    description   TEXT     NOT NULL COMMENT '描述文字',
    PRIMARY KEY (id),
    FOREIGN KEY (creator) REFERENCES user (id),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id)
) COMMENT ='实验范式';

CREATE INDEX ix_paradigm_experiment_id ON paradigm (experiment_id);

CREATE TABLE paradigm_file
(
    id           INTEGER  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified DATETIME NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted   BOOL     NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    paradigm_id  INTEGER  NOT NULL COMMENT '实验范式ID',
    file_id      INTEGER  NOT NULL COMMENT '文件ID',
    PRIMARY KEY (id),
    FOREIGN KEY (file_id) REFERENCES file (id),
    FOREIGN KEY (paradigm_id) REFERENCES paradigm (id)
) COMMENT ='实验范式文件';

CREATE INDEX ix_paradigm_file_paradigm_id ON paradigm_file (paradigm_id);

INSERT INTO alembic_version (version_num)
VALUES ('576fba37f0c3');

