CREATE TABLE eeg_data
(
    id               INTEGER                NOT NULL COMMENT '主键' AUTO_INCREMENT,
    gmt_create       DATETIME               NOT NULL COMMENT '创建时间'       DEFAULT NOW(),
    gmt_modified     DATETIME               NOT NULL COMMENT '修改时间'       DEFAULT NOW(),
    is_deleted       BOOL                   NOT NULL COMMENT '该行是否被删除' DEFAULT FALSE,
    user_id          INTEGER                NOT NULL COMMENT '用户ID',
    gender           ENUM ('male','female') NOT NULL COMMENT '性别',
    age              INTEGER                NOT NULL COMMENT '年龄',
    data_update_year DATETIME               NOT NULL COMMENT '数据上传时间',
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user (id)
) COMMENT ='脑电数据';

CREATE INDEX ix_eeg_data_user_id ON eeg_data (user_id);

UPDATE alembic_version
SET version_num='fc790ff29f0a'
WHERE alembic_version.version_num = 'a0d93a525a2a';
