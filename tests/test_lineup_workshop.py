from datetime import datetime

import pytest

from festival.artist import Artist
from festival.errors import ConflictError, InvalidValueError
from festival.performance import Lineup, Workshop
from festival.venue import Venue

CASINO = Venue("Grand Casino", 650, "Seafront")
CABANE = Venue("La Cabane", 3, "Beach")
START = datetime(2027, 6, 10, 20, 30)
PAUL = Artist("Paul Kerbrat")
NORA = Artist("Nora Lebrun")
MAX = Artist("Max Pellerin")
LEA = Artist("Léa Fontaine")
INES = Artist("Inès Moreau")


def test_lineup_lists_the_host_then_the_acts():
    gala = Lineup("Gala", CASINO, START, 90, PAUL, [NORA, MAX])
    assert gala.kind == "lineup"
    assert gala.artists() == [PAUL, NORA, MAX]
    assert gala.capacity == 650


def test_lineup_needs_at_least_two_acts():
    with pytest.raises(InvalidValueError):
        Lineup("Gala", CASINO, START, 90, PAUL, [NORA])


def test_an_act_cannot_appear_twice():
    with pytest.raises(InvalidValueError):
        Lineup("Gala", CASINO, START, 90, PAUL, [NORA, NORA])


def test_the_host_is_not_an_act():
    with pytest.raises(InvalidValueError):
        Lineup("Gala", CASINO, START, 90, PAUL, [PAUL, NORA])


def test_three_acts_need_at_least_36_minutes():
    Lineup("Gala", CASINO, START, 36, PAUL, [NORA, MAX, LEA])
    with pytest.raises(InvalidValueError):
        Lineup("Gala", CASINO, START, 35, PAUL, [NORA, MAX, LEA])


def test_workshop_places_are_limited_by_the_venue():
    workshop = Workshop("Improv", CABANE, START, 60, INES, 12)
    assert workshop.capacity == 3
    assert workshop.places_left == 3


def test_workshop_registration_ignores_case():
    workshop = Workshop("Improv", CABANE, START, 60, INES, 12, ["Camille R."])
    with pytest.raises(ConflictError):
        workshop.register("camille r.")


def test_workshop_refuses_registrations_when_full():
    workshop = Workshop("Improv", CABANE, START, 60, INES, 12, ["A", "B", "C"])
    assert workshop.places_left == 0
    with pytest.raises(ConflictError):
        workshop.register("D")


def test_workshop_needs_at_least_one_place():
    with pytest.raises(InvalidValueError):
        Workshop("Improv", CABANE, START, 60, INES, 0)
