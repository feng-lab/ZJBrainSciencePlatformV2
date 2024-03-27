-- Running upgrade a9e5944a8108 -> 134d9c7fb6e0

CREATE TABLE eegdata_file (
    dataset_id INTEGER NOT NULL COMMENT '脑电数据id', 
    path TEXT NOT NULL COMMENT '文件路径', 
    id INTEGER NOT NULL COMMENT '主键' AUTO_INCREMENT, 
    gmt_create DATETIME NOT NULL COMMENT '创建时间' DEFAULT now(), 
    gmt_modified DATETIME NOT NULL COMMENT '修改时间' DEFAULT now(), 
    is_deleted BOOL NOT NULL COMMENT '该行是否被删除' DEFAULT false, 
    PRIMARY KEY (id), 
    FOREIGN KEY(dataset_id) REFERENCES eegdata (id)
)COMMENT='脑电数据文件';

CREATE INDEX ix_eegdata_file_dataset_id ON eegdata_file (dataset_id);

ALTER TABLE eegdata COMMENT '脑电数据';

UPDATE alembic_version SET version_num='134d9c7fb6e0' WHERE alembic_version.version_num = 'a9e5944a8108';

