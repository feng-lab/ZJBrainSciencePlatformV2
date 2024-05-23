-- Running upgrade ee8f1867aa17 -> 864ccb4da84a

CREATE TABLE cumulative_data_per_month (
    date DATE NOT NULL COMMENT '日期', 
    full_data_size FLOAT COMMENT '数据总量(GB)', 
    full_data_count FLOAT COMMENT '数据条目', 
    id INTEGER NOT NULL COMMENT '主键' AUTO_INCREMENT, 
    gmt_create DATETIME NOT NULL COMMENT '创建时间' DEFAULT now(), 
    gmt_modified DATETIME NOT NULL COMMENT '修改时间' DEFAULT now(), 
    is_deleted BOOL NOT NULL COMMENT '该行是否被删除' DEFAULT false, 
    PRIMARY KEY (id)
)COMMENT='数据总量';

UPDATE alembic_version SET version_num='864ccb4da84a' WHERE alembic_version.version_num = 'ee8f1867aa17';

