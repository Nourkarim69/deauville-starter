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

    @property
    def performances(self) -> list[Performance]:
        return sorted(
            self._performances.values(),
            key=lambda performance: (performance.start, performance.venue.name),
        )

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

    def performance(self, performance_id: str) -> Performance:
        if performance_id not in self._performances:
            raise NotFoundError(f"There is no performance {performance_id!r}.")
        return self._performances[performance_id]

    def programme(self, day: date) -> list[Performance]:
        return [p for p in self.performances if p.festival_day == day]

    def add_performance(self, performance: Performance) -> None:
        self._check(performance)
        self._performances[performance.id] = performance

    def replace_performance(self, performance_id: str, new: Performance) -> None:
        self.performance(performance_id)
        self._check(new, ignore=performance_id)
        del self._performances[performance_id]
        self._performances[new.id] = new

    def remove_performance(self, performance_id: str) -> None:
        self.performance(performance_id)
        del self._performances[performance_id]

    def register(self, performance_id: str, name: str) -> Workshop:
        performance = self.performance(performance_id)
        if not isinstance(performance, Workshop):
            raise InvalidValueError(f"{performance.title} is not a workshop.")
        performance.register(name)
        return performance

    def _check(self, new: Performance, ignore: str | None = None) -> None:
        self.venue(new.venue.slug)
        for artist in new.artists():
            self.artist(artist.slug)
        if not self._first_day <= new.festival_day <= self._last_day:
            raise ConflictError(
                f"{new.title} is on {new.festival_day}, outside the festival "
                f"({self._first_day} to {self._last_day})."
            )
        for other in self._performances.values():
            if other.id == ignore:
                continue
            if not _too_close(new, other):
                continue
            if other.venue.slug == new.venue.slug:
                raise ConflictError(
                    f"{new.venue.name} is busy with {_describe(other)}. "
                    "Leave 30 minutes between two shows."
                )
            other_slugs = {artist.slug for artist in other.artists()}
            for artist in new.artists():
                if artist.slug in other_slugs:
                    raise ConflictError(
                        f"{artist.name} is busy with {_describe(other)}. "
                        "An artist needs 30 minutes between two performances."
                    )


def _too_close(a: Performance, b: Performance) -> bool:
    return a.start < b.end + BREAK and b.start < a.end + BREAK


def _describe(performance: Performance) -> str:
    return (
        f"{performance.title} "
        f"({performance.start:%Y-%m-%d %H:%M}-{performance.end:%H:%M})"
    )