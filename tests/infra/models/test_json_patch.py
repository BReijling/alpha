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
            "value": datetime.date(2015, 3, 17),
        },
    ]

    assert patch == correct_patch


def test_json_patch_with_datetime(patch_with_datetime):
    json_patch = JsonPatch(patch_with_datetime)
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


def test_json_patch_without_string(patch_without_string):
    json_patch = JsonPatch(patch_without_string)
    patch = [patch for patch in json_patch]
    assert patch == patch_without_string


def test_json_patch_with_boolean(patch_with_boolean):
    json_patch = JsonPatch(patch_with_boolean)
    patch = [patch for patch in json_patch]
    correct_patch = [
        {"op": "replace", "path": "/", "value": "string"},
        {"op": "replace", "path": "/", "value": True},
        {"op": "replace", "path": "/", "value": False},
        {"op": "replace", "path": "/", "value": True},
        {"op": "replace", "path": "/", "value": False},
    ]

    assert patch == correct_patch
