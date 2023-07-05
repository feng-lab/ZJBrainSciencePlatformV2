from test import client
from typing import Iterable

import pytest

from app.model.response import NoneResponse, Response
from app.model.schema import AtlasInfo

test_atlas = {
    "name": "test atlas",
    "url": "https://example.com",
    "title": "测试脑图谱",
    "whole_segment_id": 114514,
}


@pytest.fixture(scope="function")
def created_atlas_id(logon_root_headers: dict[str, str]) -> Iterable[int]:
    r = client.post("/api/createAtlas", headers=logon_root_headers, json=test_atlas)
    assert r.is_success
    ro = Response[int](**r.json())
    assert ro.code == 0
    assert ro.data > 0

    yield ro.data

    r = client.delete("/api/deleteAtlas", headers=logon_root_headers, json={"id": (ro.data)})
    assert r.is_success
    assert NoneResponse(**r.json()).code == 0


def test_get_atlas_info(created_atlas_id: int, logon_root_headers: dict[str, str]):
    r = client.get(f"/api/getAtlasInfo?atlas_id={created_atlas_id}", headers=logon_root_headers)
    assert r.is_success
    ro = Response[AtlasInfo](**r.json())
    assert ro.code == 0
    assert ro.data.dict() == test_atlas


def test_update_atlas(created_atlas_id: int, logon_root_headers: dict[str, str]):
    update_atlas = {
        "id": created_atlas_id,
        "name": "new name",
        "url": "new url",
        "title": "new title",
        "whole_segment_id": None,
    }
    r = client.post("/api/updateAtlas", headers=logon_root_headers, json=update_atlas)
    assert r.is_success
    assert NoneResponse(**r.json()).code == 0

    r = client.get(
        "/api/getAtlasInfo", params={"atlas_id": created_atlas_id}, headers=logon_root_headers
    )
    assert r.is_success
    ro = Response[AtlasInfo](**r.json())
    assert ro.code == 0
    assert ro.data.dict() | {"id": created_atlas_id} == update_atlas
