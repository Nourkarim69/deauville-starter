import shutil

import pytest
from fastapi.testclient import TestClient

from festival.api import create_app
from festival.storage import JsonStorage


@pytest.fixture
def client(tmp_path):
    copy = tmp_path / "festival.json"
    shutil.copy("data/festival.json", copy)
    return TestClient(create_app(JsonStorage(copy)))


def gala(**changes):
    body = {
        "kind": "lineup",
        "title": "Gala",
        "venue": "grand-casino",
        "start": "2027-06-13T10:00",
        "duration_minutes": 90,
        "host": "paul-kerbrat",
        "acts": ["nora-lebrun", "max-pellerin"],
    }
    body.update(changes)
    return body


def test_festival_and_lists(client):
    assert client.get("/api/festival").json()["days"][0] == "2027-06-10"
    assert len(client.get("/api/venues").json()) == 4
    assert len(client.get("/api/artists").json()) == 12


def test_programme_of_a_day_and_a_venue(client):
    shows = client.get("/api/programme?day=2027-06-11&venue=le-kiosque").json()
    assert [show["id"] for show in shows][-1] == "le-kiosque-2027-06-12-0100"


def test_a_bad_day_is_refused_by_fastapi(client):
    response = client.get("/api/programme?day=June 11")
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


def test_unknown_things_give_404(client):
    assert client.get("/api/artists/nobody").status_code == 404
    assert client.get("/api/performances/nothing").status_code == 404


def test_now(client):
    now = client.get("/api/now?at=2027-06-11T21:00").json()
    assert now["now_playing"][0]["title"] == "Tall Tales"
    assert len(now["up_next"]) == 3


def test_create_move_and_delete_a_performance(client):
    created = client.post("/api/performances", json=gala())
    assert created.status_code == 201
    assert created.json()["summary"] == "hosted by Paul Kerbrat, with Nora Lebrun, Max Pellerin"
    moved = client.put(
        "/api/performances/grand-casino-2027-06-13-1000", json=gala(start="2027-06-13T12:00")
    )
    assert moved.json()["id"] == "grand-casino-2027-06-13-1200"
    assert client.delete("/api/performances/grand-casino-2027-06-13-1200").status_code == 204


def test_a_busy_venue_gives_409_and_changes_nothing(client):
    response = client.post("/api/performances", json=gala(start="2027-06-10T21:00"))
    assert response.status_code == 409
    assert "Grand Casino is busy" in response.json()["detail"]


def test_an_invalid_value_gives_422(client):
    response = client.post("/api/performances", json=gala(acts=["nora-lebrun"]))
    assert response.status_code == 422


def test_every_change_is_saved(tmp_path):
    copy = tmp_path / "festival.json"
    shutil.copy("data/festival.json", copy)
    TestClient(create_app(JsonStorage(copy))).post("/api/artists", json={"name": "Zoé Test"})
    assert "zoe-test" in [a.slug for a in JsonStorage(copy).load().artists]


def test_register_a_participant(client):
    response = client.post(
        "/api/performances/la-cabane-2027-06-11-1030/participants", json={"name": "Nour K."}
    )
    assert response.status_code == 201
    assert "Nour K." in response.json()["participants"]


def test_the_website_is_served(client):
    assert "<html" in client.get("/").text.lower()
    assert client.get("/admin/").status_code == 200