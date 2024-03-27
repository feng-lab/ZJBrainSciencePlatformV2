-- Running upgrade a0d93a525a2a -> a9e5944a8108

CREATE TABLE eegdata (
    user_id INTEGER NOT NULL COMMENT '用户ID', 
    gender ENUM('male','female') NOT NULL COMMENT '性别', 
    age INTEGER NOT NULL COMMENT '年龄', 
    data_update_year DATETIME NOT NULL COMMENT '数据上传时间', 
    id INTEGER NOT NULL COMMENT '主键' AUTO_INCREMENT, 
    gmt_create DATETIME NOT NULL COMMENT '创建时间' DEFAULT now(), 
    gmt_modified DATETIME NOT NULL COMMENT '修改时间' DEFAULT now(), 
    is_deleted BOOL NOT NULL COMMENT '该行是否被删除' DEFAULT false, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES user (id)
)COMMENT='数据集';

CREATE INDEX ix_eegdata_user_id ON eegdata (user_id);

UPDATE alembic_version SET version_num='a9e5944a8108' WHERE alembic_version.version_num = 'a0d93a525a2a';

