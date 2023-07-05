from test import client

import pytest

from app.model.response import Response


@pytest.mark.parametrize("whole_segment_id", [114514, None])
def test_create_atlas(whole_segment_id: int | None, logon_root_headers: dict[str, str]) -> None:
    create_atlas = {
        "name": "test atlas",
        "url": "https://example.com",
        "title": "测试脑图谱",
        "whole_segment_id": whole_segment_id,
    }
    r = client.post("/api/createAtlas", headers=logon_root_headers, json=create_atlas)
    assert r.is_success
    ro = Response[int](**r.json())
    assert ro.code == 0
    assert ro.data > 0
