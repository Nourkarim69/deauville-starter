import json
import os
from abc import ABC, abstractmethod
from datetime import date, datetime
from pathlib import Path
from typing import Any

from festival.artist import Artist
from festival.errors import FestivalError, StorageError
from festival.festival import Festival
from festival.performance import Lineup, Performance, Solo, Workshop
from festival.venue import Venue


class Storage(ABC):
    @abstractmethod
    def load(self) -> Festival:
        ...

    @abstractmethod
    def save(self, festival: Festival) -> None:
        ...


class JsonStorage(Storage):
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def load(self) -> Festival:
        try:
            with open(self._path, encoding="utf-8") as file:
                data = json.load(file)
        except OSError as error:
            raise StorageError(f"Cannot read {self._path}: {error.strerror}.") from error
        except json.JSONDecodeError as error:
            raise StorageError(
                f"{self._path} is not valid JSON (line {error.lineno})."
            ) from error
        try:
            return _festival_from_dict(data)
        except (KeyError, TypeError, ValueError) as error:
            raise StorageError(f"{self._path} is broken: {_explain(error)}") from error
        except FestivalError as error:
            raise StorageError(f"{self._path} breaks a rule: {error}") from error

    def save(self, festival: Festival) -> None:
        temporary = self._path.with_suffix(".tmp")
        try:
            with open(temporary, "w", encoding="utf-8") as file:
                json.dump(_festival_to_dict(festival), file, ensure_ascii=False, indent=2)
                file.write("\n")
            os.replace(temporary, self._path)
        except OSError as error:
            raise StorageError(f"Cannot write {self._path}: {error.strerror}.") from error


def _explain(error: Exception) -> str:
    if isinstance(error, KeyError):
        return f"the field {error.args[0]!r} is missing."
    return f"{error}."


def _festival_from_dict(data: dict[str, Any]) -> Festival:
    festival = Festival(
        data["name"],
        date.fromisoformat(data["first_day"]),
        date.fromisoformat(data["last_day"]),
    )
    for item in data["venues"]:
        festival.add_venue(Venue(item["name"], item["capacity"], item["address"]))
    for item in data["artists"]:
        festival.add_artist(
            Artist(item["name"], item.get("bio", ""), item.get("photo_url", ""))
        )
    for item in data["performances"]:
        festival.add_performance(performance_from_dict(festival, item))
    return festival


def performance_from_dict(festival: Festival, item: dict[str, Any]) -> Performance:
    common = {
        "title": item["title"],
        "venue": festival.venue(item["venue"]),
        "start": datetime.fromisoformat(item["start"]),
        "duration_minutes": item["duration_minutes"],
        "description": item.get("description", ""),
    }
    kind = item["kind"]
    if kind == "solo":
        return Solo(artist=festival.artist(item["artist"]),
                    min_age=item.get("min_age", 0), **common)
    if kind == "lineup":
        return Lineup(host=festival.artist(item["host"]),
                      acts=[festival.artist(slug) for slug in item["acts"]], **common)
    if kind == "workshop":
        return Workshop(teacher=festival.artist(item["teacher"]),
                        max_participants=item["max_participants"],
                        participants=item.get("participants", []), **common)
    raise ValueError(f"unknown kind of performance {kind!r}")


def _festival_to_dict(festival: Festival) -> dict[str, Any]:
    return {
        "name": festival.name,
        "first_day": festival.first_day.isoformat(),
        "last_day": festival.last_day.isoformat(),
        "venues": [
            {"name": venue.name, "capacity": venue.capacity, "address": venue.address}
            for venue in festival.venues
        ],
        "artists": [
            {"name": artist.name, "bio": artist.bio, "photo_url": artist.photo_url}
            for artist in festival.artists
        ],
        "performances": [_performance_to_dict(p) for p in festival.performances],
    }


def _performance_to_dict(performance: Performance) -> dict[str, Any]:
    item: dict[str, Any] = {
        "kind": performance.kind,
        "title": performance.title,
        "venue": performance.venue.slug,
        "start": performance.start.isoformat(timespec="minutes"),
        "duration_minutes": performance.duration_minutes,
        "description": performance.description,
    }
    if isinstance(performance, Solo):
        item["artist"] = performance.artist.slug
        item["min_age"] = performance.min_age
    elif isinstance(performance, Lineup):
        item["host"] = performance.host.slug
        item["acts"] = [act.slug for act in performance.acts]
    elif isinstance(performance, Workshop):
        item["teacher"] = performance.teacher.slug
        item["max_participants"] = performance.max_participants
        item["participants"] = performance.participants
    return item