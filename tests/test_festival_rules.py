from datetime import date, datetime

import pytest

from festival.artist import Artist
from festival.errors import ConflictError, InvalidValueError, NotFoundError
from festival.festival import Festival
from festival.performance import Solo, Workshop
from festival.venue import Venue

KIOSQUE = Venue("Le Kiosque", 120, "Beach promenade")
CASINO = Venue("Grand Casino", 650, "Seafront")
NORA = Artist("Nora Lebrun")
MAX = Artist("Max Pellerin")


def make_festival():
    festival = Festival("Deauville", date(2027, 6, 10), date(2027, 6, 13))
    for venue in (KIOSQUE, CASINO):
        festival.add_venue(venue)
    for artist in (NORA, MAX):
        festival.add_artist(artist)
    return festival


def solo(start, venue=KIOSQUE, artist=NORA, duration=60, title="After Hours"):
    return Solo(title, venue, datetime.fromisoformat(start), duration, artist)


def test_a_performance_can_be_added_and_found():
    festival = make_festival()
    festival.add_performance(solo("2027-06-12T01:00"))
    assert festival.performance("le-kiosque-2027-06-12-0100").title == "After Hours"


def test_the_programme_of_a_day_includes_shows_after_midnight():
    festival = make_festival()
    festival.add_performance(solo("2027-06-11T21:00"))
    festival.add_performance(solo("2027-06-12T01:00", artist=MAX))
    assert len(festival.programme(date(2027, 6, 11))) == 2


def test_a_performance_must_be_during_the_festival():
    with pytest.raises(ConflictError):
        make_festival().add_performance(solo("2027-06-14T21:00"))


def test_a_venue_needs_30_minutes_between_two_shows():
    festival = make_festival()
    festival.add_performance(solo("2027-06-12T01:00"))
    with pytest.raises(ConflictError, match="Le Kiosque is busy with After Hours"):
        festival.add_performance(solo("2027-06-12T02:20", artist=MAX))
    festival.add_performance(solo("2027-06-12T02:30", artist=MAX))


def test_an_artist_needs_30_minutes_between_two_shows_anywhere():
    festival = make_festival()
    festival.add_performance(solo("2027-06-11T21:00"))
    with pytest.raises(ConflictError, match="Nora Lebrun is busy"):
        festival.add_performance(solo("2027-06-11T22:15", venue=CASINO))


def test_the_artists_must_be_known_by_the_festival():
    with pytest.raises(NotFoundError):
        make_festival().add_performance(solo("2027-06-11T21:00", artist=Artist("Nobody")))


def test_moving_onto_a_busy_slot_changes_nothing():
    festival = make_festival()
    festival.add_performance(solo("2027-06-11T21:00"))
    festival.add_performance(solo("2027-06-11T21:00", venue=CASINO, artist=MAX))
    with pytest.raises(ConflictError):
        festival.replace_performance(
            "le-kiosque-2027-06-11-2100", solo("2027-06-11T21:00", venue=CASINO)
        )
    assert festival.performance("le-kiosque-2027-06-11-2100").venue == KIOSQUE


def test_only_a_workshop_takes_registrations():
    festival = make_festival()
    festival.add_performance(solo("2027-06-11T21:00"))
    with pytest.raises(InvalidValueError):
        festival.register("le-kiosque-2027-06-11-2100", "Camille R.")
    festival.add_performance(
        Workshop("Improv", CASINO, datetime(2027, 6, 11, 10, 0), 60, MAX, 12)
    )
    workshop = festival.register("grand-casino-2027-06-11-1000", "Camille R.")
    assert workshop.participants == ["Camille R."]