from datetime import date

import pytest

from festival.artist import Artist
from festival.errors import ConflictError, InvalidValueError, NotFoundError
from festival.festival import Festival
from festival.venue import Venue


def make_festival():
    return Festival("Deauville Festival du Rire", date(2027, 6, 10), date(2027, 6, 13))


def test_festival_lists_its_days():
    assert make_festival().days == [
        date(2027, 6, 10),
        date(2027, 6, 11),
        date(2027, 6, 12),
        date(2027, 6, 13),
    ]


def test_festival_cannot_end_before_it_starts():
    with pytest.raises(InvalidValueError):
        Festival("Oops", date(2027, 6, 13), date(2027, 6, 10))


def test_venues_keep_the_order_they_were_added_in():
    festival = make_festival()
    festival.add_venue(Venue("Le Kiosque", 120, "Beach"))
    festival.add_venue(Venue("Grand Casino", 650, "Seafront"))
    assert [venue.slug for venue in festival.venues] == ["le-kiosque", "grand-casino"]


def test_artists_are_sorted_by_slug():
    festival = make_festival()
    festival.add_artist(Artist("Hugo Lemaire"))
    festival.add_artist(Artist("Élodie Marchal"))
    assert [artist.slug for artist in festival.artists] == [
        "elodie-marchal",
        "hugo-lemaire",
    ]


def test_two_artists_with_the_same_slug_are_the_same_artist():
    festival = make_festival()
    festival.add_artist(Artist("Élodie Marchal"))
    with pytest.raises(ConflictError):
        festival.add_artist(Artist("elodie marchal"))


def test_an_unknown_artist_is_not_found():
    with pytest.raises(NotFoundError):
        make_festival().artist("nobody")
