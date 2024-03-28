-- Running upgrade 46b22297d54e -> 0380cb81acd2

CREATE TABLE eegdata_file (
    eegdata_id INTEGER NOT NULL COMMENT '脑电数据的id', 
    path TEXT NOT NULL COMMENT '文件路径', 
    id INTEGER NOT NULL COMMENT '主键' AUTO_INCREMENT, 
    gmt_create DATETIME NOT NULL COMMENT '创建时间' DEFAULT now(), 
    gmt_modified DATETIME NOT NULL COMMENT '修改时间' DEFAULT now(), 
    is_deleted BOOL NOT NULL COMMENT '该行是否被删除' DEFAULT false, 
    PRIMARY KEY (id), 
    FOREIGN KEY(eegdata_id) REFERENCES eegdata (id)
)COMMENT='数据集文件';

CREATE INDEX ix_eegdata_file_eegdata_id ON eegdata_file (eegdata_id);

UPDATE alembic_version SET version_num='0380cb81acd2' WHERE alembic_version.version_num = '46b22297d54e';

