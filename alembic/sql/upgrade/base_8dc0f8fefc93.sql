CREATE TABLE alembic_version
(
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 8dc0f8fefc93

CREATE TABLE atlas
(
    name             VARCHAR(255) NOT NULL COMMENT '名称',
    url              VARCHAR(255) NOT NULL COMMENT '主页地址',
    title            VARCHAR(255) NOT NULL COMMENT '页面显示的标题',
    whole_segment_id BIGINT COMMENT '全脑轮廓ID',
    id               INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create       DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified     DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted       BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    PRIMARY KEY (id)
) COMMENT ='脑图谱';

CREATE TABLE atlas_behavioral_domain
(
    name         VARCHAR(255) NOT NULL COMMENT '名称',
    value        DOUBLE       NOT NULL COMMENT '值',
    label        VARCHAR(255) NOT NULL COMMENT '显示的名字',
    description  TEXT COMMENT '描述',
    parent_id    INTEGER COMMENT '父节点ID，null表示第一层节点',
    id           INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted   BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    atlas_id     INTEGER      NOT NULL COMMENT '所属图谱ID',
    PRIMARY KEY (id)
) COMMENT ='脑图谱的行为域结构数据，以树状结构存储';

CREATE TABLE atlas_paradigm_class
(
    name         VARCHAR(255) NOT NULL COMMENT '名称',
    value        DOUBLE       NOT NULL COMMENT '值',
    label        VARCHAR(255) NOT NULL COMMENT '标签',
    description  TEXT         NOT NULL COMMENT '描述',
    parent_id    INTEGER COMMENT '父节点ID，null表示第一层节点',
    id           INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted   BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    atlas_id     INTEGER      NOT NULL COMMENT '所属图谱ID',
    PRIMARY KEY (id)
) COMMENT ='脑图谱范例集';

CREATE TABLE atlas_region
(
    region_id    BIGINT COMMENT '脑区ID',
    description  VARCHAR(255) NOT NULL COMMENT '描述',
    acronym      VARCHAR(255) NOT NULL COMMENT '缩写',
    lobe         VARCHAR(255) COMMENT '所属脑叶',
    gyrus        VARCHAR(255) COMMENT '所属脑回',
    label        VARCHAR(255) COMMENT '标签',
    parent_id    INTEGER COMMENT '父节点ID，null表示第一层节点',
    id           INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted   BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    atlas_id     INTEGER      NOT NULL COMMENT '所属图谱ID',
    PRIMARY KEY (id)
) COMMENT ='脑图谱脑区构成信息，以树状结构存储';

CREATE TABLE atlas_region_behavioral_domain
(
    `key`        VARCHAR(255) NOT NULL COMMENT '行为域',
    value        DOUBLE       NOT NULL COMMENT '行为域值',
    region_id    BIGINT       NOT NULL COMMENT '脑区ID',
    id           INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted   BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    atlas_id     INTEGER      NOT NULL COMMENT '所属图谱ID',
    PRIMARY KEY (id)
) COMMENT ='脑图谱中与脑区相关联的行为域数据';

CREATE TABLE atlas_region_link
(
    link_id        INTEGER      NOT NULL COMMENT '连接信息ID',
    region1        VARCHAR(255) NOT NULL COMMENT '脑区1',
    region2        VARCHAR(255) NOT NULL COMMENT '脑区2',
    value          DOUBLE COMMENT '连接强度，null表示仅有连接',
    opposite_value DOUBLE COMMENT '反向连接强度，null表示仅有连接',
    id             INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create     DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified   DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted     BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    atlas_id       INTEGER      NOT NULL COMMENT '所属图谱ID',
    PRIMARY KEY (id)
) COMMENT ='脑图谱脑区之间的连接强度信息';

CREATE TABLE atlas_region_paradigm_class
(
    `key`        VARCHAR(255) NOT NULL COMMENT '范例集',
    value        DOUBLE       NOT NULL COMMENT '范例集值',
    region_id    BIGINT       NOT NULL COMMENT '脑区ID',
    id           INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted   BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    atlas_id     INTEGER      NOT NULL COMMENT '所属图谱ID',
    PRIMARY KEY (id)
) COMMENT ='脑图谱中与脑区相关联的范例集';

CREATE TABLE device
(
    brand        VARCHAR(255) NOT NULL COMMENT '设备品牌',
    name         VARCHAR(255) NOT NULL COMMENT '设备名称',
    purpose      VARCHAR(255) NOT NULL COMMENT '设备用途',
    id           INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted   BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    PRIMARY KEY (id)
) COMMENT ='实验设备';

CREATE TABLE human_subject_index
(
    `index` INTEGER NOT NULL COMMENT '下一个被试者的序号' AUTO_INCREMENT,
    PRIMARY KEY (`index`)
) COMMENT ='被试者用户序号';

CREATE TABLE user
(
    username         VARCHAR(255) NOT NULL COMMENT '用户名',
    hashed_password  VARCHAR(255) NOT NULL COMMENT '密码哈希',
    staff_id         VARCHAR(255) NOT NULL COMMENT '员工号',
    last_login_time  DATETIME COMMENT '上次登录时间',
    last_logout_time DATETIME COMMENT '上次下线时间',
    access_level     INTEGER      NOT NULL COMMENT '权限级别',
    id               INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create       DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified     DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted       BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    PRIMARY KEY (id)
) COMMENT ='用户';

CREATE INDEX ix_user_staff_id ON user (staff_id);

CREATE INDEX ix_user_username ON user (username);

CREATE TABLE experiment
(
    name             VARCHAR(255)                         NOT NULL COMMENT '实验名称',
    type             ENUM ('other','SSVEP','MI','neuron') NOT NULL COMMENT '实验类型',
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
    id               INTEGER                              NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create       DATETIME                             NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified     DATETIME                             NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted       BOOL                                 NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    PRIMARY KEY (id),
    FOREIGN KEY (main_operator) REFERENCES user (id)
) COMMENT ='实验';

CREATE INDEX ix_experiment_start_at ON experiment (start_at);

CREATE TABLE human_subject
(
    user_id        INTEGER  NOT NULL COMMENT '用户ID',
    name           VARCHAR(50) COMMENT '姓名',
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
    id             INTEGER  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create     DATETIME NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified   DATETIME NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted     BOOL     NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user (id)
) COMMENT ='被试者';

CREATE UNIQUE INDEX ix_human_subject_user_id ON human_subject (user_id);

CREATE TABLE notification
(
    gmt_create   DATETIME                  NOT NULL COMMENT '创建时间'       DEFAULT now(),
    type         ENUM ('task_step_status') NOT NULL COMMENT '消息类型',
    creator      INTEGER                   NOT NULL COMMENT '消息发送者ID',
    receiver     INTEGER                   NOT NULL COMMENT '消息接收者ID',
    status       ENUM ('unread','read')    NOT NULL COMMENT '消息状态',
    content      TEXT                      NOT NULL COMMENT '消息内容',
    id           INTEGER                   NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_modified DATETIME                  NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted   BOOL                      NOT NULL COMMENT '该行是否被删除' DEFAULT false,
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

CREATE TABLE experiment_tag
(
    experiment_id INTEGER     NOT NULL COMMENT '实验ID',
    tag           VARCHAR(50) NOT NULL COMMENT '标签',
    PRIMARY KEY (experiment_id, tag),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id)
) COMMENT ='实验标签';

CREATE TABLE paradigm
(
    experiment_id INTEGER  NOT NULL COMMENT '实验ID',
    creator       INTEGER  NOT NULL COMMENT '创建者ID',
    description   TEXT     NOT NULL COMMENT '描述文字',
    id            INTEGER  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create    DATETIME NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified  DATETIME NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted    BOOL     NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    PRIMARY KEY (id),
    FOREIGN KEY (creator) REFERENCES user (id),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id)
) COMMENT ='实验范式';

CREATE TABLE virtual_file
(
    experiment_id INTEGER      NOT NULL COMMENT '实验ID',
    paradigm_id   INTEGER COMMENT '范式ID，null表示不属于范式而属于实验',
    name          VARCHAR(255) NOT NULL COMMENT '文件名',
    file_type     VARCHAR(50)  NOT NULL COMMENT '文件类型',
    is_original   BOOL         NOT NULL COMMENT '是否是设备产生的原始文件',
    size          FLOAT        NOT NULL COMMENT '显示给用户看的文件大小',
    id            INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create    DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified  DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted    BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    PRIMARY KEY (id),
    FOREIGN KEY (experiment_id) REFERENCES experiment (id),
    FOREIGN KEY (paradigm_id) REFERENCES paradigm (id)
) COMMENT ='虚拟文件';

CREATE INDEX ix_virtual_file_experiment_id ON virtual_file (experiment_id);

CREATE INDEX ix_virtual_file_paradigm_id ON virtual_file (paradigm_id);

CREATE TABLE storage_file
(
    virtual_file_id INTEGER      NOT NULL COMMENT '虚拟文件ID',
    name            VARCHAR(255) NOT NULL COMMENT '文件名',
    size            FLOAT        NOT NULL COMMENT '文件大小',
    storage_path    VARCHAR(255) NOT NULL COMMENT '文件系统存储路径',
    id              INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create      DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified    DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted      BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    PRIMARY KEY (id),
    FOREIGN KEY (virtual_file_id) REFERENCES virtual_file (id)
) COMMENT ='实际文件';

CREATE INDEX ix_storage_file_virtual_file_id ON storage_file (virtual_file_id);

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
    is_deleted   BOOL                                                     NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    PRIMARY KEY (id),
    FOREIGN KEY (creator) REFERENCES user (id),
    FOREIGN KEY (source_file) REFERENCES virtual_file (id)
) COMMENT ='任务';

CREATE TABLE task_step
(
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
    id             INTEGER                                                  NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create     DATETIME                                                 NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified   DATETIME                                                 NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted     BOOL                                                     NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    PRIMARY KEY (id),
    FOREIGN KEY (result_file_id) REFERENCES virtual_file (id),
    FOREIGN KEY (task_id) REFERENCES task (id)
) COMMENT ='任务步骤';

INSERT INTO alembic_version (version_num)
VALUES ('8dc0f8fefc93');

