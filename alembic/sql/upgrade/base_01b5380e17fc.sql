CREATE TABLE alembic_version
(
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);


CREATE TABLE device
(
    id           INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted   BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    brand        VARCHAR(255) NOT NULL COMMENT '设备品牌',
    name         VARCHAR(255) NOT NULL COMMENT '设备名称',
    purpose      VARCHAR(255) NOT NULL COMMENT '设备用途',
    PRIMARY KEY (id)
) COMMENT ='实验设备';

CREATE TABLE human_subject_index
(
    `index` INTEGER NOT NULL COMMENT '下一个被试者的序号' AUTO_INCREMENT,
    PRIMARY KEY (`index`)
) COMMENT ='被试者用户序号';

CREATE TABLE user
(
    id               INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create       DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified     DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted       BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    username         VARCHAR(255) NOT NULL COMMENT '用户名',
    hashed_password  VARCHAR(255) NOT NULL COMMENT '密码哈希',
    staff_id         VARCHAR(255) NOT NULL COMMENT '员工号',
    last_login_time  DATETIME COMMENT '上次登录时间',
    last_logout_time DATETIME COMMENT '上次下线时间',
    access_level     INTEGER      NOT NULL COMMENT '权限级别',
    PRIMARY KEY (id)
) COMMENT ='用户';
CREATE INDEX ix_user_staff_id ON user (staff_id);
CREATE INDEX ix_user_username ON user (username);

CREATE TABLE experiment
(
    id               INTEGER                              NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create       DATETIME                             NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified     DATETIME                             NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted       BOOL                                 NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    name             VARCHAR(255)                         NOT NULL COMMENT '实验名称',
    type             ENUM ('SSVEP','MI','neuron','other') NOT NULL COMMENT '实验类型',
    description      TEXT                                 NOT NULL COMMENT '实验描述',
    location         VARCHAR(255)                         NOT NULL COMMENT '实验地点',
    start_at         DATETIME                             NOT NULL COMMENT '实验开始时间',
    end_at           DATETIME                             NOT NULL COMMENT '实验结束时间',
    main_operator    INTEGER                              NOT NULL COMMENT '主操作者ID',
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

CREATE TABLE human_subject
(
    id             INTEGER  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create     DATETIME NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified   DATETIME NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted     BOOL     NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    user_id        INTEGER  NOT NULL COMMENT '用户ID',
    gender         ENUM ('male','female') COMMENT '性别',
    birthdate      DATE COMMENT '出生日期',
    death_date     DATE COMMENT '死亡日期',
    education      VARCHAR(50) COMMENT '教育程度',
    occupation     VARCHAR(50) COMMENT '职业',
    marital_status ENUM ('unmarried','married') COMMENT '婚姻状况',
    abo_blood_type ENUM ('A','B','AB','O') COMMENT 'ABO血型',
    is_left_handed BOOL COMMENT '是否是左撇子',
    phone_number   VARCHAR(50) COMMENT '电话号码',
    email          VARCHAR(100) COMMENT '电子邮箱地址',
    address        VARCHAR(255) COMMENT '住址',
    name           VARCHAR(50) COMMENT '姓名',
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user (id)
) COMMENT ='被试者';
CREATE UNIQUE INDEX ix_human_subject_user_id ON human_subject (user_id);

CREATE TABLE notification
(
    id           INTEGER                   NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME                  NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified DATETIME                  NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted   BOOL                      NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
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
    user_id       INTEGER NOT NULL,
    experiment_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, experiment_id),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id),
    FOREIGN KEY (user_id) REFERENCES user (id)
) COMMENT ='实验助手关系';

CREATE TABLE experiment_device
(
    experiment_id INTEGER NOT NULL,
    device_id     INTEGER NOT NULL,
    `index`       INTEGER NOT NULL COMMENT '实验内序号',
    PRIMARY KEY (experiment_id, device_id),
    FOREIGN KEY (device_id) REFERENCES device (id),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id)
) COMMENT ='实验包含的设备';

CREATE TABLE experiment_human_subject
(
    experiment_id INTEGER NOT NULL,
    user_id       INTEGER NOT NULL,
    PRIMARY KEY (experiment_id, user_id),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id),
    FOREIGN KEY (user_id) REFERENCES human_subject (user_id)
) COMMENT ='实验包含的被试者';

CREATE TABLE paradigm
(
    id            INTEGER  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create    DATETIME NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified  DATETIME NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted    BOOL     NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    experiment_id INTEGER  NOT NULL COMMENT '实验ID',
    creator       INTEGER  NOT NULL COMMENT '创建者ID',
    description   TEXT     NOT NULL COMMENT '描述文字',
    PRIMARY KEY (id),
    FOREIGN KEY (creator) REFERENCES user (id),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id)
) COMMENT ='实验范式';

CREATE TABLE file
(
    id            INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create    DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified  DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted    BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    experiment_id INTEGER      NOT NULL COMMENT '实验ID',
    paradigm_id   INTEGER COMMENT '范式ID，null表示不属于范式而属于实验',
    name          VARCHAR(255) NOT NULL COMMENT '逻辑路径',
    extension     VARCHAR(50)  NOT NULL COMMENT '文件扩展名',
    size          FLOAT        NOT NULL COMMENT '同一实验下的文件序号',
    is_original   BOOL         NOT NULL COMMENT '是否是设备产生的原始文件',
    PRIMARY KEY (id),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id),
    FOREIGN KEY (paradigm_id) REFERENCES paradigm (id)
) COMMENT ='文件';
CREATE INDEX ix_file_experiment_id ON file (experiment_id);
CREATE INDEX ix_file_paradigm_id ON file (paradigm_id);

CREATE TABLE task
(
    id           INTEGER                                                  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME                                                 NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified DATETIME                                                 NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted   BOOL                                                     NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    name         VARCHAR(255)                                             NOT NULL COMMENT '任务名',
    description  TEXT                                                     NOT NULL COMMENT '任务描述',
    source_file  INTEGER                                                  NOT NULL COMMENT '任务分析的文件ID',
    type         ENUM ('preprocess','analysis','preprocess_analysis')     NOT NULL COMMENT '任务类型',
    start_at     DATETIME COMMENT '任务开始执行的时间',
    end_at       DATETIME COMMENT '任务结束时间',
    status       ENUM ('wait_start','running','done','error','cancelled') NOT NULL COMMENT '任务状态',
    creator      INTEGER                                                  NOT NULL COMMENT '任务创建者ID',
    PRIMARY KEY (id),
    FOREIGN KEY (creator) REFERENCES user (id),
    FOREIGN KEY (source_file) REFERENCES file (id)
) COMMENT ='任务';

CREATE TABLE task_step
(
    id             INTEGER                                                  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create     DATETIME                                                 NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified   DATETIME                                                 NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted     BOOL                                                     NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
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
    FOREIGN KEY (task_id) REFERENCES task (id),
    FOREIGN KEY (result_file_id) REFERENCES file (id)
) COMMENT ='任务步骤';

CREATE TABLE experiment_tag
(
    experiment_id INTEGER     NOT NULL COMMENT '实验ID',
    tag           VARCHAR(50) NOT NULL COMMENT '标签',
    PRIMARY KEY (experiment_id, tag),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id)
) COMMENT ='实验标签';

INSERT INTO alembic_version (version_num)
VALUES ('01b5380e17fc');
