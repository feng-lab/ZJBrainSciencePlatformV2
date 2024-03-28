-- Running upgrade 8dc0f8fefc93 -> 46b22297d54e

CREATE TABLE dataset (
    user_id INTEGER NOT NULL COMMENT '用户ID', 
    description TEXT NOT NULL COMMENT '描述', 
    species TEXT COMMENT '物种', 
    paper_title TEXT COMMENT '文章标题', 
    paper_doi TEXT COMMENT '文章DOI', 
    development_stage TEXT COMMENT '发育时期', 
    file_format TEXT COMMENT '文件格式', 
    sample_count INTEGER COMMENT '样本数量', 
    data_publisher TEXT COMMENT '数据发布机构/单位', 
    data_update_year DATE COMMENT '数据更新年份', 
    file_count INTEGER COMMENT '文件数量', 
    file_total_size_gb FLOAT COMMENT '数据总量(GB)', 
    file_acquired_size_gb FLOAT COMMENT '已获取数据(GB)', 
    associated_diseases TEXT COMMENT '相关疾病', 
    organ TEXT COMMENT '器官', 
    cell_count INTEGER COMMENT '细胞数', 
    data_type TEXT COMMENT '数据类型', 
    experiment_platform TEXT COMMENT '实验、测序平台', 
    fetch_url TEXT COMMENT '下载路径', 
    project TEXT COMMENT '项目', 
    id INTEGER NOT NULL COMMENT '主键' AUTO_INCREMENT, 
    gmt_create DATETIME NOT NULL COMMENT '创建时间' DEFAULT now(), 
    gmt_modified DATETIME NOT NULL COMMENT '修改时间' DEFAULT now(), 
    is_deleted BOOL NOT NULL COMMENT '该行是否被删除' DEFAULT false, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES user (id)
)COMMENT='数据集';

CREATE INDEX ix_dataset_user_id ON dataset (user_id);

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
)COMMENT='脑电数据';

CREATE INDEX ix_eegdata_user_id ON eegdata (user_id);

CREATE TABLE dataset_file (
    dataset_id INTEGER NOT NULL COMMENT '数据集id', 
    path TEXT NOT NULL COMMENT '文件路径', 
    id INTEGER NOT NULL COMMENT '主键' AUTO_INCREMENT, 
    gmt_create DATETIME NOT NULL COMMENT '创建时间' DEFAULT now(), 
    gmt_modified DATETIME NOT NULL COMMENT '修改时间' DEFAULT now(), 
    is_deleted BOOL NOT NULL COMMENT '该行是否被删除' DEFAULT false, 
    PRIMARY KEY (id), 
    FOREIGN KEY(dataset_id) REFERENCES dataset (id)
)COMMENT='数据集文件';

CREATE INDEX ix_dataset_file_dataset_id ON dataset_file (dataset_id);

UPDATE alembic_version SET version_num='46b22297d54e' WHERE alembic_version.version_num = '8dc0f8fefc93';

