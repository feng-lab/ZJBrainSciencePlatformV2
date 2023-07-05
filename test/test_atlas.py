from test import client

import pytest

from app.model.response import NoneResponse, Response
from app.model.schema import AtlasInfo

test_atlas = {
    "name": "test atlas",
    "url": "https://example.com",
    "title": "测试脑图谱",
    "whole_segment_id": 114514,
}


@pytest.fixture(scope="module")
def created_atlas_id(logon_root_headers: dict[str, str]) -> int:
    r = client.post("/api/createAtlas", headers=logon_root_headers, json=test_atlas)
    assert r.is_success
    ro = Response[int](**r.json())
    assert ro.code == 0
    assert ro.data > 0
    atlas_id = ro.data

    yield atlas_id

    r = client.delete("/api/deleteAtlas", headers=logon_root_headers, json={"id": atlas_id})
    assert r.is_success
    ro = NoneResponse(**r.json())
    assert ro.code == 0


def test_get_atlas_info(created_atlas_id: int, logon_root_headers: dict[str, str]):
    r = client.get(
        "/api/getAtlasInfo/", headers=logon_root_headers, params={"atlas_id": created_atlas_id}
    )
    assert r.is_success
    ro = Response[AtlasInfo](**r.json())
    assert ro.code == 0
    assert ro.data.dict() == test_atlas
