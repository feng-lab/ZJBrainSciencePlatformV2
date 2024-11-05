import io
import json
import logging
import os
from datetime import datetime
from pathlib import Path, PurePath, PurePosixPath
from typing import BinaryIO
from urllib.parse import quote

import numpy as np
import oss2
import pandas as pd
from fastapi import UploadFile
from oss2 import SizedFileAdapter, determine_part_size
from oss2.models import PartInfo

from app.common.config import config
from app.common.exception import ServiceError
from app.common.localization import Entity
from app.common.test_data_visualization.test_data_visualization import encode_matrix_fbs
from app.model.schema import DatasetDirectoryTreeNode

logger = logging.getLogger(__name__)
auth = oss2.Auth(config.ACCESS_KEY_ID, config.ACCESS_KEY_SECRET)


def bucket_auth(auth=auth, endpoint_url=config.ENDPOINT_URL, bucket_name=config.BUCKET_NAME):
    return oss2.Bucket(auth, endpoint_url, bucket_name)


def create_dir(bucket, remote_fp=None):
    bucket.put_object(remote_fp, "")
    logger.info(f"create directory {remote_fp} success")


def upload_file(bucket, remote_fp: str, local_fp: str):
    bucket.put_object_from_file(remote_fp, local_fp)


def download_file(bucket, remote_fp: str, local_fp: str):
    if not bucket.object_exists(remote_fp):
        raise ServiceError.not_found({remote_fp})
    bucket.get_object_to_file(remote_fp, local_fp)


def oos_file_upload(bucket, remote_fp: str, reader: BinaryIO, file_size: int) -> None:
    if bucket.object_exists(remote_fp) and bucket.head_object(remote_fp).content_length == file_size:
        logger.info(f"the oos file{remote_fp} is existed")
    else:
        try:
            bucket.put_object(str(remote_fp), reader)
            logger.info(f"sample uploading oos file {remote_fp} successfully")
        except oss2.exceptions.NoSuchKey as e:
            logger.error(f"put_object failed,status={e.status}")
            preferred_size = 10 * 1024 * 1024
            part_size = determine_part_size(file_size, preferred_size=preferred_size)
            upload_id = bucket.init_multipart_upload(remote_fp).upload_id
            parts = []

            part_number = 1
            offset = 0
            while offset < file_size:
                part_data = reader.read(preferred_size)
                num_to_upload = min(part_size, file_size - offset)
                # if not part_data:
                #     break
                # num_to_upload = min(part_size, file_size - offset)
                # 调用SizedFileAdapter(fileobj, size)方法会生成一个新的文件对象，重新计算起始追加位置。
                result = bucket.upload_part(remote_fp, upload_id, part_number, part_data)
                parts.append(PartInfo(part_number, result.etag))

                offset += num_to_upload
                part_number += 1
            headers = dict()
            # 设置文件访问权限ACL。此处设置为OBJECT_ACL_PRIVATE，表示私有权限。
            # headers["x-oss-object-acl"] = oss2.OBJECT_ACL_PRIVATE
            bucket.complete_multipart_upload(remote_fp, upload_id, parts, headers=headers)
            logger.info(f"multipart uploading oos file {remote_fp} successfully")


def stream_download(bucket, remote_fp: str):
    # print(remote_fp)
    remote_fp = str(remote_fp)
    filename = os.path.basename(remote_fp)
    filetype = os.path.splitext(remote_fp)[-1]
    params = {
        "response-content-disposition": f'attachment; filename="{filename}"',
        "Accept-Encoding": "gzip",
        "Content-Type": filetype or "text/plain",
    }  # , '
    object_stream = bucket.get_object(quote(remote_fp), params=params)

    return object_stream


def resumble_download(bucket, remote_fp: str, local_fp: str = None):
    remote_fp = str(remote_fp)
    filename = os.path.basename(remote_fp)
    filetype = os.path.splitext(remote_fp)[-1]
    if local_fp is None:
        local_fp = f"C:\\Users\\admin\\Downloads\\{filename}"
    oss2.defaults.connection_pool_size = 4
    params = {
        "response-content-disposition": f'attachment; filename="{filename}"',
        "Accept-Encoding": "gzip",
        "Content-Type": filetype or "text/plain",
    }
    oss2.resumable_download(bucket, remote_fp, local_fp, params=params)


def object_ls(bucket, remote_fp="") -> list:
    files_list = []

    for obj in oss2.ObjectIteratorV2(bucket, prefix=remote_fp, delimiter="/", start_after=remote_fp):
        obj_key = str(obj.key)
        file_name = obj_key.replace(str(remote_fp), "").rstrip("/")

        if obj.last_modified is not None:
            last_modified = datetime.utcfromtimestamp(obj.last_modified)
            formatted_date = last_modified.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            formatted_date = None
        if obj.is_prefix():  # 判断obj为文件夹。
            files_list.append({"type": "directory", "name": file_name, "last_modified": formatted_date, "size": None})
        else:  # 判断obj为文件。
            files_list.append({"type": "file", "name": file_name, "last_modified": formatted_date, "size": obj.size})
    return files_list


def walk_dataset_directory_tree_oss(bucket, prefix):
    directory_tree = []
    for obj in oss2.ObjectIteratorV2(bucket, prefix=prefix, delimiter="/"):
        if obj.is_prefix():
            node = DatasetDirectoryTreeNode(
                name=obj.key.replace(str(prefix), "").rstrip("/"),
                dirs=walk_dataset_directory_tree_oss(bucket, obj.key) or [],
            )
            directory_tree.append(node)
    return directory_tree


def object_size_Byte(bucket, remote_fp: str = "") -> float:
    length = 0
    for obj in oss2.ObjectIteratorV2(bucket, prefix=remote_fp):
        length += obj.size
    return length


def delete_object_oss(bucket, remote_fp: str) -> None:
    for b in oss2.ObjectIteratorV2(bucket, prefix=remote_fp):
        bucket.delete_object(b.key)
        logger.info(f"Deleted {b.key}")


def delet_dir_oss(bucket, remote_fp: str) -> None:
    for obj in oss2.ObjectIterator(bucket, prefix=remote_fp):
        bucket.delete_object(obj.key)


def rename_object(bucket, remote_fp: str, new_name: str) -> None:
    # 实际执行 复制删除

    if not bucket.object_exists(remote_fp):
        logger.error(f"file {remote_fp} is not exist")
        raise ServiceError.not_found(Entity.dataset)

    bucket.copy_object(config.BUCKET_NAME, remote_fp, new_name)
    bucket.delete_object(remote_fp)
    logger.info(f"rename object {remote_fp} to {new_name}")


def bucket_list_delete(bucket, list_name: list):
    bucket.batch_delete_objects(list_name)


def file_resumable_upload(bucket, remote_fp, local_fp):
    oss2.resumable_upload(bucket, remote_fp, local_fp, multipart_threshold=100 * 1024)


def upload_big_multipart_file(bucket, local_fp, remote_fp, partsize=500):
    partsize = partsize * 1024 * 1024
    total_size = os.path.getsize(local_fp)
    part_size = oss2.determine_part_size(total_size, preferred_size=partsize)
    # 初始化分片上传，得到Upload ID。接下来的接口都要用到这个Upload ID�?
    upload_id = bucket.init_multipart_upload(remote_fp).upload_id
    # 逐个上传分片
    # 其中oss2.SizedFileAdapter()把fileobj转换为一个新的文件对象，新的文件对象可读的长度等于size_to_upload
    with open(local_fp, "rb") as fileobj:
        parts = []
        part_number = 1
        offset = 0
        while offset < total_size:
            size_to_upload = min(part_size, total_size - offset)
            result = bucket.upload_part(
                remote_fp, upload_id, part_number, oss2.SizedFileAdapter(fileobj, size_to_upload)
            )
            parts.append(oss2.models.PartInfo(part_number, result.etag, size=size_to_upload, part_crc=result.crc))

            offset += size_to_upload
            part_number += 1

        # 完成分片上传
        bucket.complete_multipart_upload(remote_fp, upload_id, parts)


def upload_dir_folder(dir_lo_path="", dir_oss_path=""):
    if not os.path.exists(dir_lo_path):
        raise ValueError("file path not exist")
    basename = os.path.basename(dir_lo_path.rstrip("/"))
    paths = os.walk(dir_lo_path)
    for path, _, file_ls in paths:
        bucket = bucket_auth()
        for filename in file_ls:
            file_path = os.path.relpath(os.path.join(path, filename), dir_lo_path).replace("\\", "/")
            local_fp = os.path.join(path, filename)
            if not dir_oss_path.endswith("/"):
                dir_oss_path = dir_oss_path + "/"
            if dir_lo_path.endswith("/"):
                oss_file_dir = dir_oss_path + file_path
            else:
                oss_file_dir = dir_oss_path + basename + "/" + file_path

            if (
                bucket.object_exists(oss_file_dir)
                and os.path.getsize(local_fp) == bucket.get_object_meta(oss_file_dir).content_length
            ):
                continue
            try:
                upload_file(bucket, oss_file_dir, local_fp)
            except Exception as e:
                upload_big_multipart_file(bucket, local_fp, oss_file_dir, 2048)


#
def CalculateFolderLength(bucket, path) -> int:
    length = 0
    for obj in oss2.ObjectIterator(bucket, prefix=path):
        length += obj.size
    return length


def list_directory_by_path(bucket, path) -> list:
    result = []
    for obj in oss2.ObjectIterator(bucket, prefix=path, delimiter="/"):
        if obj.is_prefix():  # 判断obj为文件夹。
            length = CalculateFolderLength(bucket, obj.key)
            result.append({"type": "directory", "name": obj.key, "size": length})
        else:  # 判断obj为文件。
            result.append({"type": "file", "name": obj.key, "size": obj.size})
    return result


def remove_extension2json(filename):
    return os.path.splitext(filename)[0] + ".json"


cached_data = {}


def get_oss_object(bucket, remote_fp: str):
    try:
        c = bucket.get_object(remote_fp)
        content = c.read()

        # 将字节内容解码为字符串
        json_str = content.decode("utf-8")

        # 将 JSON 字符串解析为字典
        # data = json.loads(json_str)
        return json_str
    except:
        raise ServiceError.remote_service_error(f"fail to access")


def cache_data(func):
    global cached_data

    def wrapper(*args, **kwargs):
        global cached_data
        if cached_data is None:
            # Fetch data from OSS if it hasn't been cached yet
            cached_data = func(*args, **kwargs)
        return cached_data

    return wrapper


# @cache_data
def get_data_from_oss(bucket, remote_fp: str) -> dict:
    if remote_fp in cached_data:
        return cached_data[remote_fp]
    json_str = get_oss_object(bucket, remote_fp)
    data = json.loads(json_str)
    cached_data[remote_fp] = data
    return data


def data2bytes(json_info, layout_name: str):
    try:
        data = json_info.get(layout_name)

        # print(layout_name)
        # print(type(np.shape(data)))
        if len(np.shape(data)) == 2:
            tsne_array = np.array(data)
            # print(tsne_array)
            # layout_data = []
            # layout_data.append(pd.DataFrame(tsne_array, columns=[f"{layout_name}_0", f"{layout_name}_1"]))
            # df = pd.concat(layout_data, axis=1, copy=False)
            # print(np.shape(tsne_array)[1])
            df = pd.DataFrame(tsne_array, columns=[f"{layout_name}_0", f"{layout_name}_1"])
            # print(df)

        elif len(np.shape(data)) == 1:
            # print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            df = pd.DataFrame(data, columns=[f"{layout_name}"])

        else:
            raise ServiceError.params_error(layout_name)
        rs = encode_matrix_fbs(df, col_idx=df.columns, row_idx=None)
        # print(rs)
        return io.BytesIO(rs)

    except:
        raise ServiceError.params_error(layout_name)
