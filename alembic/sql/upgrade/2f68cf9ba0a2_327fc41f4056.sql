CREATE TABLE message_localization
(
    id           INTEGER                NOT NULL COMMENT '主键' AUTO_INCREMENT,
    message_id   VARCHAR(50)            NOT NULL COMMENT '消息模板ID',
    locale       ENUM ('zh_CN','en_US') NOT NULL COMMENT '消息语言',
    template     VARCHAR(255)           NOT NULL COMMENT '消息模板内容',
    gmt_create   DATETIME               NOT NULL COMMENT '创建时间'       DEFAULT now(),
    gmt_modified DATETIME               NOT NULL COMMENT '修改时间'       DEFAULT now(),
    is_deleted   BOOL                   NOT NULL COMMENT '该行是否被删除' DEFAULT false,
    PRIMARY KEY (id)
) COMMENT ='本地化消息';

CREATE UNIQUE INDEX ix_message_localization_message_id ON message_localization (message_id);

UPDATE alembic_version
SET version_num='327fc41f4056'
WHERE alembic_version.version_num = '2f68cf9ba0a2';

