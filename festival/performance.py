from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta

from festival.artist import Artist
from festival.errors import InvalidValueError
from festival.text import clean_name
from festival.venue import Venue

DAY_ENDS_AT_HOUR = 6


class Performance(ABC):
    def __init__(self, title: str, venue: Venue, start: datetime,
                 duration_minutes: int, description: str = "") -> None:
        self._title = clean_name(title, "performance title")
        if not 1 <= duration_minutes <= 360:
            raise InvalidValueError(
                f"A performance lasts from 1 to 360 minutes, not {duration_minutes}."
            )
        self._venue = venue
        self._start = start
        self._duration_minutes = duration_minutes
        self._description = description.strip()

    @property
    def title(self) -> str:
        return self._title

    @property
    def venue(self) -> Venue:
        return self._venue

    @property
    def start(self) -> datetime:
        return self._start

    @property
    def duration_minutes(self) -> int:
        return self._duration_minutes

    @property
    def description(self) -> str:
        return self._description

    @property
    def end(self) -> datetime:
        return self._start + timedelta(minutes=self._duration_minutes)

    @property
    def id(self) -> str:
        return f"{self._venue.slug}-{self._start:%Y-%m-%d-%H%M}"

    @property
    def festival_day(self) -> date:
        return (self._start - timedelta(hours=DAY_ENDS_AT_HOUR)).date()

    @property
    @abstractmethod
    def kind(self) -> str:
        ...

    @abstractmethod
    def artists(self) -> list[Artist]:
        ...


class Solo(Performance):
    def __init__(self, title: str, venue: Venue, start: datetime,
                 duration_minutes: int, artist: Artist, min_age: int = 0,
                 description: str = "") -> None:
        super().__init__(title, venue, start, duration_minutes, description)
        if not 0 <= min_age <= 18:
            raise InvalidValueError(f"The minimum age goes from 0 to 18, not {min_age}.")
        self._artist = artist
        self._min_age = min_age

    @property
    def kind(self) -> str:
        return "solo"

    @property
    def artist(self) -> Artist:
        return self._artist

    @property
    def min_age(self) -> int:
        return self._min_age

    def artists(self) -> list[Artist]:
        return [self._artist]