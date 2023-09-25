from test import client
from typing import Iterable

import pytest

from app.model.schema import AtlasInfo

test_atlas = {"name": "test atlas", "url": "https://example.com", "title": "测试脑图谱", "whole_segment_id": 114514}


@pytest.fixture(scope="function")
def created_atlas_id(logon_root_headers: dict[str, str]) -> Iterable[int]:
    atlas_id = client.request_with_test("POST", "/api/createAtlas", int, json=test_atlas, headers=logon_root_headers)
    yield atlas_id
    _ = client.request_with_test(
        "DELETE", "/api/deleteAtlas", type(None), headers=logon_root_headers, json={"id": atlas_id}
    )


def test_get_atlas_info(created_atlas_id: int, logon_root_headers: dict[str, str]):
    atlas_info = client.request_with_test(
        "GET", "/api/getAtlasInfo", AtlasInfo, params={"atlas_id": created_atlas_id}, headers=logon_root_headers
    )
    assert atlas_info.id > 0 and not atlas_info.is_deleted
    assert atlas_info.dict(include=set(test_atlas.keys())) == test_atlas


def test_update_atlas(created_atlas_id: int, logon_root_headers: dict[str, str]):
    update_atlas = {
        "id": created_atlas_id,
        "name": "new name",
        "url": "new url",
        "title": "new title",
        "whole_segment_id": None,
    }
    client.request_with_test("POST", "/api/updateAtlas", type(None), headers=logon_root_headers, json=update_atlas)

    atlas_info = client.request_with_test(
        "GET", "/api/getAtlasInfo", AtlasInfo, params={"atlas_id": created_atlas_id}, headers=logon_root_headers
    )
    assert atlas_info.id > 0 and not atlas_info.is_deleted
    assert atlas_info.dict(include=set(update_atlas.keys())) == update_atlas
