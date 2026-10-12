import pytest

from festival.errors import InvalidValueError
from festival.venue import Venue


def test_venue_cleans_its_name_and_builds_its_slug():
    venue = Venue("  Théâtre des Planches ", 320, "Town centre")
    assert venue.name == "Théâtre des Planches"
    assert venue.slug == "theatre-des-planches"


def test_venue_refuses_an_empty_name():
    with pytest.raises(InvalidValueError):
        Venue("   ", 100, "Somewhere")


def test_venue_needs_at_least_one_seat():
    with pytest.raises(InvalidValueError):
        Venue("Le Kiosque", 0, "Beach promenade")
