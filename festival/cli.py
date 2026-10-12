import argparse
import sys
from datetime import date, datetime

from festival.errors import FestivalError
from festival.festival import Festival
from festival.performance import Performance
from festival.storage import JsonStorage

DATA_FILE = "data/festival.json"


def parse_day(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a day, use e.g. 2027-06-11")


def parse_moment(text: str) -> datetime:
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{text!r} is not a moment, use e.g. 2027-06-11T21:00"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deauville Festival du Rire")
    commands = parser.add_subparsers(dest="command", required=True)

    programme = commands.add_parser("programme", help="the programme of one day")
    programme.add_argument("day", type=parse_day, help="e.g. 2027-06-11")

    commands.add_parser("artists", help="the artists and their number of shows")

    now = commands.add_parser("now", help="what is on stage, and the next 3 shows")
    now.add_argument("--at", type=parse_moment, help="e.g. 2027-06-11T21:00")

    args = parser.parse_args(argv)
    try:
        festival = JsonStorage(DATA_FILE).load()
        if args.command == "programme":
            show_programme(festival, args.day)
        elif args.command == "artists":
            show_artists(festival)
        else:
            show_now(festival, args.at or datetime.now())
    except FestivalError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


def show_programme(festival: Festival, day: date) -> None:
    performances = festival.programme(day)
    print(f"Programme of {day}")
    if not performances:
        print("  nothing on this day")
    for performance in performances:
        print("  " + line(performance))


def show_artists(festival: Festival) -> None:
    for artist in festival.artists:
        count = len(festival.performances_of(artist.slug))
        print(f"  {artist.name:<20} {count} show{'s' if count != 1 else ''}")


def show_now(festival: Festival, at: datetime) -> None:
    print(f"On stage at {at:%Y-%m-%d %H:%M}")
    playing = festival.now_playing(at)
    if not playing:
        print("  nothing right now")
    for performance in playing:
        print("  " + line(performance))
    print("Up next")
    upcoming = festival.up_next(at)
    if not upcoming:
        print("  nothing more")
    for performance in upcoming:
        print("  " + line(performance))


def line(performance: Performance) -> str:
    names = ", ".join(artist.name for artist in performance.artists())
    return (
        f"{performance.start:%a %d %H:%M}-{performance.end:%H:%M}  "
        f"{performance.venue.name:<22} {performance.title} ({performance.kind}: {names})"
    )