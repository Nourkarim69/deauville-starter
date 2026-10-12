import json

import pytest

from festival.errors import StorageError
from festival.storage import JsonStorage

DATA = "data/festival.json"


def test_the_real_data_file_loads():
    festival = JsonStorage(DATA).load()
    assert festival.name == "Deauville Festival du Rire 2027"
    assert len(festival.venues) == 4
    assert len(festival.artists) == 12
    assert len(festival.performances) == 23


def test_saving_then_loading_gives_the_same_festival(tmp_path):
    original = JsonStorage(DATA).load()
    copy = JsonStorage(tmp_path / "festival.json")
    copy.save(original)
    reloaded = copy.load()
    assert [v.slug for v in reloaded.venues] == [v.slug for v in original.venues]
    assert [a.slug for a in reloaded.artists] == [a.slug for a in original.artists]
    assert [p.id for p in reloaded.performances] == [p.id for p in original.performances]


def test_a_missing_file_gives_a_clear_error(tmp_path):
    with pytest.raises(StorageError, match="Cannot read"):
        JsonStorage(tmp_path / "nothing.json").load()


def test_a_file_that_is_not_json_gives_a_clear_error(tmp_path):
    broken = tmp_path / "festival.json"
    broken.write_text("{ not json", encoding="utf-8")
    with pytest.raises(StorageError, match="not valid JSON"):
        JsonStorage(broken).load()


def test_a_file_with_a_missing_field_gives_a_clear_error(tmp_path):
    broken = tmp_path / "festival.json"
    broken.write_text('{"name": "Deauville"}', encoding="utf-8")
    with pytest.raises(StorageError, match="first_day"):
        JsonStorage(broken).load()


def test_a_file_that_breaks_a_rule_gives_a_clear_error(tmp_path):
    with open(DATA, encoding="utf-8") as file:
        data = json.load(file)
    data["performances"][0]["duration_minutes"] = 0
    broken = tmp_path / "festival.json"
    broken.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(StorageError, match="breaks a rule"):
        JsonStorage(broken).load()