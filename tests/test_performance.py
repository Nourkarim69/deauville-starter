from datetime import date, datetime

import pytest

from festival.artist import Artist
from festival.errors import InvalidValueError
from festival.performance import Performance, Solo
from festival.venue import Venue

KIOSQUE = Venue("Le Kiosque", 120, "Beach promenade")
NORA = Artist("Nora Lebrun")


def make_solo(start="2027-06-12T01:00", duration=60, min_age=0):
    return Solo(
        "After Hours", KIOSQUE, datetime.fromisoformat(start), duration, NORA, min_age
    )


def test_a_performance_cannot_be_created_directly():
    with pytest.raises(TypeError):
        Performance("Show", KIOSQUE, datetime(2027, 6, 11, 21, 0), 60)


def test_solo_computes_its_id_and_its_end():
    solo = make_solo()
    assert solo.id == "le-kiosque-2027-06-12-0100"
    assert solo.end == datetime(2027, 6, 12, 2, 0)


def test_a_show_after_midnight_belongs_to_the_day_before():
    assert make_solo().festival_day == date(2027, 6, 11)


def test_duration_must_be_between_1_and_360_minutes():
    with pytest.raises(InvalidValueError):
        make_solo(duration=0)
    with pytest.raises(InvalidValueError):
        make_solo(duration=361)


def test_minimum_age_must_be_between_0_and_18():
    with pytest.raises(InvalidValueError):
        make_solo(min_age=19)
