import logging
import os
from itertools import islice
from pathlib import Path, PurePath, PurePosixPath
from urllib.parse import quote

import oss2

from app.common.config import config

logger = logging.getLogger(__name__)
auth = oss2.Auth(config.ACCESS_KEY_ID, config.ACCESS_KEY_SECRET)


def bucket_auth(auth=auth, endpoint_url=config.ENDPOINT_URL, bucket_name=config.BUCKET_NAME):
    return oss2.Bucket(auth, endpoint_url, bucket_name)


def create_dir(bucket, remote_fp=None):
    if not isinstance(remote_fp, str) or not remote_fp.endswith("/"):
        raise ValueError("romote_fp must be a string and end with /")
    bucket.put_object(remote_fp, "")


def upload_file(bucket, remote_fp: str, local_fp: str):
    bucket.put_object_from_file(remote_fp, local_fp)


def download_file(bucket, remote_fp: str, local_fp: str):
    if not bucket.object_exists(remote_fp):
        raise ValueError(f"oss file {remote_fp} is not exist")
    bucket.get_object_to_file(remote_fp, local_fp)


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


def object_ls(bucket, remote_fp="") -> list[str]:
    objects = []
    for b in oss2.ObjectIteratorV2(bucket, prefix=remote_fp):
        objects.append(b.key)
    return objects


def object_size_Byte(bucket, remote_fp="") -> int:
    length = 0
    for obj in oss2.ObjectIteratorV2(bucket, prefix=remote_fp):
        length += obj.size
        print(obj.key)
    return length


def delete_object_oss(bucket, remote_fp: str) -> None:
    bucket.delete_object(remote_fp)
    assert not bucket.object_exists(remote_fp)


def delet_dir_oss(bucket, remote_fp: str) -> None:
    for obj in oss2.ObjectIterator(bucket, prefix=remote_fp):
        bucket.delete_object(obj.key)


def rename_object(bucket, remote_fp: str, new_name: str) -> None:
    # 实际执行 复制删除
    result = bucket.copy_object(config.BUCKET_NAME, remote_fp, new_name)
    if not result.status == 200:
        raise ValueError("not success")
    result_del = bucket.delete_object(remote_fp)
    # if result_del.status ==200:
    #     print('rename done')


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


def upload_oss_file(bucket, local_fp: str, remote_fp: str):
    if not os.path.exists(local_fp):
        raise ValueError(f"local_file {local_fp} is not exist")
    basename = os.path.basename(local_fp)
    remote_fp = str(PurePosixPath(remote_fp, basename))
    print(local_fp, remote_fp)
    try:
        print(1)
        upload_file(bucket, remote_fp, local_fp)
    except:
        upload_big_multipart_file(bucket, local_fp, remote_fp, partsize=500)


def upload_dir_folder(dir_lo_path="", dir_oss_path=""):
    # 上传文件，为最后名新建文件夹子�?
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
            # 上传
            # print(oss_file_dir)
            if (
                bucket.object_exists(oss_file_dir)
                and os.path.getsize(local_fp) == bucket.get_object_meta(oss_file_dir).content_length
            ):
                # print(f"{os.path.join(path, filename)} has existed")
                continue
            try:
                upload_file(bucket, oss_file_dir, local_fp)
            except Exception as e:
                # print(f'try to use multipart upload, {e}')
                # print(f'{os.path.join(path, filename)}')
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
