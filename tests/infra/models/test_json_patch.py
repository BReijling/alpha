import datetime

from alpha.infra.models.json_patch import JsonPatch


def test_json_patch_with_date(patch_with_date):
    json_patch = JsonPatch(patch_with_date)
    patch = [patch for patch in json_patch]
    correct_patch = [
        {"op": "replace", "path": "/", "value": "string"},
        {
            "op": "replace",
            "path": "/",
            "value": datetime.datetime(2015, 3, 17, 13, 0, 0),
        },
    ]

    assert patch == correct_patch


def test_json_patch_without_date(patch_without_date):
    json_patch = JsonPatch(patch_without_date)
    patch = [patch for patch in json_patch]
    correct_patch = [
        {"op": "replace", "path": "/", "value": 1},
        {"op": "replace", "path": "/", "value": {}},
    ]
    assert patch == correct_patch
