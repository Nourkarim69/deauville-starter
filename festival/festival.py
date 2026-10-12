from datetime import date, timedelta

from festival.artist import Artist
from festival.errors import ConflictError, InvalidValueError, NotFoundError
from festival.performance import Performance, Workshop
from festival.text import clean_name
from festival.venue import Venue

BREAK = timedelta(minutes=30)


class Festival:
    def __init__(self, name: str, first_day: date, last_day: date) -> None:
        self._name = clean_name(name, "festival name")
        if last_day < first_day:
            raise InvalidValueError(
                f"The festival cannot end ({last_day}) before it starts ({first_day})."
            )
        self._first_day = first_day
        self._last_day = last_day
        self._venues: dict[str, Venue] = {}
        self._artists: dict[str, Artist] = {}
        self._performances: dict[str, Performance] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def first_day(self) -> date:
        return self._first_day

    @property
    def last_day(self) -> date:
        return self._last_day

    @property
    def days(self) -> list[date]:
        count = (self._last_day - self._first_day).days + 1
        return [self._first_day + timedelta(days=i) for i in range(count)]

    @property
    def venues(self) -> list[Venue]:
        return list(self._venues.values())

    @property
    def artists(self) -> list[Artist]:
        return sorted(self._artists.values(), key=lambda artist: artist.slug)

    def add_venue(self, venue: Venue) -> None:
        if venue.slug in self._venues:
            raise ConflictError(f"The venue {venue.name} already exists.")
        self._venues[venue.slug] = venue

    def add_artist(self, artist: Artist) -> None:
        if artist.slug in self._artists:
            raise ConflictError(f"The artist {artist.name} already exists.")
        self._artists[artist.slug] = artist

    def venue(self, slug: str) -> Venue:
        if slug not in self._venues:
            raise NotFoundError(f"There is no venue {slug!r}.")
        return self._venues[slug]

    def artist(self, slug: str) -> Artist:
        if slug not in self._artists:
            raise NotFoundError(f"There is no artist {slug!r}.")
        return self._artists[slug]