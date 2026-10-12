import pytest

from festival.artist import Artist
from festival.errors import InvalidValueError


def test_artist_cleans_its_name_and_builds_its_slug():
    artist = Artist("  Élodie  Marchal ! ")
    assert artist.name == "Élodie  Marchal !"
    assert artist.slug == "elodie-marchal"


def test_artist_bio_and_photo_are_optional():
    artist = Artist("Nora Lebrun")
    assert artist.bio == ""
    assert artist.photo_url == ""


def test_artist_refuses_an_empty_name():
    with pytest.raises(InvalidValueError):
        Artist("   ")


def test_artist_refuses_a_name_without_letters():
    with pytest.raises(InvalidValueError):
        Artist("!!!")