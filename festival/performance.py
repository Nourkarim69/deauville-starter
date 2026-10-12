from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta

from festival.artist import Artist
from festival.errors import ConflictError, InvalidValueError
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
    def capacity(self) -> int:
        return self._venue.capacity

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


class Lineup(Performance):
    def __init__(self, title: str, venue: Venue, start: datetime,
                 duration_minutes: int, host: Artist, acts: list[Artist],
                 description: str = "") -> None:
        super().__init__(title, venue, start, duration_minutes, description)
        if len(acts) < 2:
            raise InvalidValueError(f"{self.title} needs at least 2 acts, not {len(acts)}.")
        slugs = [act.slug for act in acts]
        if len(set(slugs)) != len(slugs):
            raise InvalidValueError(f"An act appears twice in {self.title}.")
        if host.slug in slugs:
            raise InvalidValueError(f"{host.name} hosts {self.title} and cannot also be an act.")
        minimum = len(acts) * 10 + (len(acts) - 1) * 3
        if duration_minutes < minimum:
            raise InvalidValueError(
                f"{self.title} has {len(acts)} acts and needs at least {minimum} minutes, "
                f"not {duration_minutes}."
            )
        self._host = host
        self._acts = list(acts)

    @property
    def kind(self) -> str:
        return "lineup"

    @property
    def host(self) -> Artist:
        return self._host

    @property
    def acts(self) -> list[Artist]:
        return list(self._acts)

    def artists(self) -> list[Artist]:
        return [self._host] + self._acts


class Workshop(Performance):
    def __init__(self, title: str, venue: Venue, start: datetime,
                 duration_minutes: int, teacher: Artist, max_participants: int,
                 participants: list[str] | None = None,
                 description: str = "") -> None:
        super().__init__(title, venue, start, duration_minutes, description)
        if max_participants < 1:
            raise InvalidValueError(
                f"{self.title} needs at least 1 participant place, not {max_participants}."
            )
        self._teacher = teacher
        self._max_participants = max_participants
        self._participants: list[str] = []
        for name in participants or []:
            self.register(name)

    @property
    def kind(self) -> str:
        return "workshop"

    @property
    def teacher(self) -> Artist:
        return self._teacher

    @property
    def max_participants(self) -> int:
        return self._max_participants

    @property
    def participants(self) -> list[str]:
        return list(self._participants)

    @property
    def capacity(self) -> int:
        return min(self._max_participants, self.venue.capacity)

    @property
    def places_left(self) -> int:
        return self.capacity - len(self._participants)

    def artists(self) -> list[Artist]:
        return [self._teacher]

    def register(self, name: str) -> None:
        cleaned = clean_name(name, "participant name")
        for participant in self._participants:
            if participant.lower() == cleaned.lower():
                raise ConflictError(f"{cleaned} is already registered for {self.title}.")
        if self.places_left == 0:
            raise ConflictError(f"{self.title} is full ({self.capacity} places).")
        self._participants.append(cleaned)