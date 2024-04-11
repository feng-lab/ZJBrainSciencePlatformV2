-- Running upgrade fc790ff29f0a -> 6c54801bec54

CREATE TABLE species (
    chinese_name TEXT NOT NULL COMMENT '中文名称', 
    english_name TEXT NOT NULL COMMENT '英文名称', 
    latin_name VARCHAR(255) NOT NULL COMMENT '拉丁文名称', 
    id INTEGER NOT NULL COMMENT '主键' AUTO_INCREMENT, 
    gmt_create DATETIME NOT NULL COMMENT '创建时间' DEFAULT now(), 
    gmt_modified DATETIME NOT NULL COMMENT '修改时间' DEFAULT now(), 
    is_deleted BOOL NOT NULL COMMENT '该行是否被删除' DEFAULT false, 
    PRIMARY KEY (id), 
    UNIQUE (latin_name)
)COMMENT='物种名称';

UPDATE alembic_version SET version_num='6c54801bec54' WHERE alembic_version.version_num = 'fc790ff29f0a';

