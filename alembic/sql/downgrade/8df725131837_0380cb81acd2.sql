-- Running downgrade 8df725131837 -> 0380cb81acd2

CREATE TABLE eegdata_file (
    eegdata_id INTEGER NOT NULL COMMENT '脑电数据的id', 
    path TEXT NOT NULL COMMENT '文件路径', 
    id INTEGER NOT NULL COMMENT '主键' AUTO_INCREMENT, 
    gmt_create DATETIME NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP, 
    gmt_modified DATETIME NOT NULL COMMENT '修改时间' DEFAULT CURRENT_TIMESTAMP, 
    is_deleted TINYINT(1) NOT NULL COMMENT '该行是否被删除' DEFAULT '0', 
    PRIMARY KEY (id), 
    CONSTRAINT eegdata_file_ibfk_1 FOREIGN KEY(eegdata_id) REFERENCES eegdata (id)
)DEFAULT CHARSET=utf8mb4 COMMENT='数据集文件' ENGINE=InnoDB COLLATE utf8mb4_0900_ai_ci;

CREATE INDEX ix_eegdata_file_eegdata_id ON eegdata_file (eegdata_id);

UPDATE alembic_version SET version_num='0380cb81acd2' WHERE alembic_version.version_num = '8df725131837';

