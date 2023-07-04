CREATE TABLE atlas
(
    id               INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create       DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified     DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted       BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    name             VARCHAR(255) NOT NULL COMMENT '名称',
    url              VARCHAR(255) NOT NULL COMMENT '主页地址',
    title            VARCHAR(255) NOT NULL COMMENT '页面显示的标题',
    whole_segment_id BIGINT       NULL COMMENT '全脑轮廓ID',
    PRIMARY KEY (id)
) COMMENT ='脑图谱';

CREATE TABLE atlas_region
(
    id           INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted   BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    region_id    BIGINT       NULL COMMENT '脑区ID',
    description  VARCHAR(255) NOT NULL COMMENT '描述',
    acronym      VARCHAR(255) NOT NULL COMMENT '缩写',
    lobe         VARCHAR(255) NULL COMMENT '所属脑叶',
    gyrus        VARCHAR(255) NULL COMMENT '所属脑回',
    parent_id    INTEGER      NULL COMMENT '父节点ID，null表示第一层节点',
    atlas_id     INTEGER      NOT NULL COMMENT '所属图谱ID',
    PRIMARY KEY (id)
) COMMENT ='脑图谱脑区构成信息，以树状结构存储';

CREATE TABLE atlas_region_link
(
    id             INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create     DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified   DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted     BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    link_id        INTEGER      NOT NULL COMMENT '连接信息ID',
    region1        VARCHAR(255) NOT NULL COMMENT '脑区1',
    region2        VARCHAR(255) NOT NULL COMMENT '脑区2',
    value          DOUBLE       NULL COMMENT '连接强度，null表示仅有连接',
    opposite_value DOUBLE       NULL COMMENT '反向连接强度，null表示仅有连接',
    atlas_id       INTEGER      NOT NULL COMMENT '所属图谱ID',
    PRIMARY KEY (id)
) COMMENT ='脑图谱脑区之间的连接强度信息';

CREATE TABLE atlas_behavioral_domain
(
    id           INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted   BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    name         VARCHAR(255) NOT NULL COMMENT '名称',
    value        DOUBLE       NOT NULL COMMENT '值',
    label        VARCHAR(255) NOT NULL COMMENT '显示的名字',
    description  TEXT         NULL COMMENT '描述',
    parent_id    INTEGER      NULL COMMENT '父节点ID，null表示第一层节点',
    atlas_id     INTEGER      NOT NULL COMMENT '所属图谱ID',
    PRIMARY KEY (id)
) COMMENT ='脑图谱的行为域结构数据，以树状结构存储';

CREATE TABLE atlas_region_behavioral_domain
(
    id           INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted   BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    `key`        VARCHAR(255) NOT NULL COMMENT '行为域',
    value        DOUBLE       NOT NULL COMMENT '行为域值',
    region_id    BIGINT       NOT NULL COMMENT '脑区ID',
    atlas_id     INTEGER      NOT NULL COMMENT '所属图谱ID',
    PRIMARY KEY (id)
) COMMENT ='脑图谱中与脑区相关联的行为域数据';

CREATE TABLE atlas_paradigm_class
(
    id           INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted   BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    name         VARCHAR(255) NOT NULL COMMENT '名称',
    value        DOUBLE       NOT NULL COMMENT '值',
    label        VARCHAR(255) NOT NULL COMMENT '标签',
    description  TEXT COMMENT '描述',
    atlas_id     INTEGER      NOT NULL COMMENT '所属图谱ID',
    PRIMARY KEY (id)
) COMMENT ='脑图谱范例集';

CREATE TABLE atlas_region_paradigm_class
(
    id           INTEGER      NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create   DATETIME     NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified DATETIME     NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted   BOOL         NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    `key`        VARCHAR(255) NOT NULL COMMENT '范例集',
    value        DOUBLE       NOT NULL COMMENT '范例集值',
    region_id    BIGINT       NOT NULL COMMENT '脑区ID',
    atlas_id     INTEGER      NOT NULL COMMENT '所属图谱ID',
    PRIMARY KEY (id)
) COMMENT ='脑图谱中与脑区相关联的范例集';

UPDATE alembic_version
SET version_num='f7cc9d40eef1'
WHERE alembic_version.version_num = '2f68cf9ba0a2';
