from datetime import datetime

from festival.cli import main
from festival.storage import JsonStorage


def test_programme_prints_the_shows_of_the_day_in_order(capsys):
    assert main(["programme", "2027-06-10"]) == 0
    output = capsys.readouterr().out
    assert output.index("Opening Gala") < output.index("Family Business")


def test_artists_prints_every_artist_with_their_shows(capsys):
    assert main(["artists"]) == 0
    assert len(capsys.readouterr().out.splitlines()) == 12


def test_now_shows_at_most_three_next_performances(capsys):
    assert main(["now", "--at", "2027-06-10T20:00"]) == 0
    output = capsys.readouterr().out
    assert len(output.split("Up next")[1].strip().splitlines()) == 3


def test_now_playing_and_up_next():
    festival = JsonStorage("data/festival.json").load()
    at = datetime(2027, 6, 10, 21, 0)
    assert [p.title for p in festival.now_playing(at)] == [
        "Opening Gala",
        "Family Business",
    ]
    assert len(festival.up_next(at)) == 3
