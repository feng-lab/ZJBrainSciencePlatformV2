-- Running downgrade 19f8815b6a7b -> 134d9c7fb6e0

ALTER TABLE eegdata COMMENT '数据集';

CREATE TABLE eegdata_file (
    dataset_id INTEGER NOT NULL COMMENT '脑电数据id', 
    path TEXT NOT NULL COMMENT '文件路径', 
    id INTEGER NOT NULL COMMENT '主键' AUTO_INCREMENT, 
    gmt_create DATETIME NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP, 
    gmt_modified DATETIME NOT NULL COMMENT '修改时间' DEFAULT CURRENT_TIMESTAMP, 
    is_deleted TINYINT(1) NOT NULL COMMENT '该行是否被删除' DEFAULT '0', 
    eegdata_id INTEGER NOT NULL COMMENT '脑电数据id', 
    PRIMARY KEY (id), 
    CONSTRAINT eegdata_file_ibfk_1 FOREIGN KEY(dataset_id) REFERENCES eegdata (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='脑电数据文件' COLLATE utf8mb4_0900_ai_ci;

CREATE INDEX ix_eegdata_file_dataset_id ON eegdata_file (dataset_id);

UPDATE alembic_version SET version_num='134d9c7fb6e0' WHERE alembic_version.version_num = '19f8815b6a7b';

