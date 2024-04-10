-- Running upgrade fc790ff29f0a -> 9338b137ec12

CREATE TABLE species (
    `Chinese_name` TEXT NOT NULL COMMENT '中文名称', 
    `English_name` TEXT NOT NULL COMMENT '英文名称', 
    latin_name TEXT NOT NULL COMMENT '拉丁文名称', 
    id INTEGER NOT NULL COMMENT '主键' AUTO_INCREMENT, 
    gmt_create DATETIME NOT NULL COMMENT '创建时间' DEFAULT now(), 
    gmt_modified DATETIME NOT NULL COMMENT '修改时间' DEFAULT now(), 
    is_deleted BOOL NOT NULL COMMENT '该行是否被删除' DEFAULT false, 
    PRIMARY KEY (id)
)COMMENT='物种名称';

ALTER TABLE eeg_data MODIFY data_update_year DATE NOT NULL COMMENT '数据上传时间';

UPDATE alembic_version SET version_num='9338b137ec12' WHERE alembic_version.version_num = 'fc790ff29f0a';

