-- Running downgrade f8c2dd179c39 -> 134d9c7fb6e0

ALTER TABLE eegdata_file ADD COLUMN dataset_id INTEGER NOT NULL COMMENT '脑电数据id';

