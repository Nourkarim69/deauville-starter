from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from festival.artist import Artist
from festival.errors import (
    ConflictError,
    FestivalError,
    InvalidValueError,
    NotFoundError,
    StorageError,
)
from festival.performance import Lineup, Performance, Solo, Workshop
from festival.storage import JsonStorage, Storage, performance_from_dict

WEB = Path(__file__).resolve().parent.parent / "web"
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "festival.json"

STATUS = {
    NotFoundError: 404,
    ConflictError: 409,
    InvalidValueError: 422,
    StorageError: 500,
}


class ArtistBody(BaseModel):
    name: str
    bio: str = ""
    photo_url: str = ""


class ParticipantBody(BaseModel):
    name: str


class PerformanceBody(BaseModel):
    kind: Literal["solo", "lineup", "workshop"]
    title: str
    venue: str
    start: datetime
    duration_minutes: int
    description: str = ""
    artist: str | None = None
    min_age: int = 0
    host: str | None = None
    acts: list[str] | None = None
    teacher: str | None = None
    max_participants: int | None = None
    participants: list[str] = []


def create_app(storage: Storage) -> FastAPI:
    app = FastAPI(title="Deauville Festival du Rire")
    festival = storage.load()

    @app.exception_handler(FestivalError)
    def festival_error(request: Request, error: FestivalError) -> JSONResponse:
        status = STATUS.get(type(error), 500)
        return JSONResponse(status_code=status, content={"detail": str(error)})

    def build(body: PerformanceBody) -> Performance:
        item = body.model_dump()
        item["start"] = body.start.isoformat(timespec="minutes")
        try:
            return performance_from_dict(festival, item)
        except KeyError, TypeError:
            raise InvalidValueError(f"A {body.kind} needs more information.")

    @app.get("/api/festival")
    def get_festival() -> dict[str, Any]:
        return {
            "name": festival.name,
            "first_day": festival.first_day.isoformat(),
            "last_day": festival.last_day.isoformat(),
            "days": [day.isoformat() for day in festival.days],
        }

    @app.get("/api/venues")
    def get_venues() -> list[dict[str, Any]]:
        return [venue_json(venue) for venue in festival.venues]

    @app.get("/api/artists")
    def get_artists() -> list[dict[str, Any]]:
        return [artist_json(artist) for artist in festival.artists]

    @app.get("/api/artists/{slug}")
    def get_artist(slug: str) -> dict[str, Any]:
        result = artist_json(festival.artist(slug))
        result["performances"] = [
            performance_json(p) for p in festival.performances_of(slug)
        ]
        return result

    @app.get("/api/programme")
    def get_programme(
        day: date | None = None, venue: str | None = None
    ) -> list[dict[str, Any]]:
        performances = festival.performances if day is None else festival.programme(day)
        if venue is not None:
            festival.venue(venue)
            performances = [p for p in performances if p.venue.slug == venue]
        return [performance_json(p) for p in performances]

    @app.get("/api/performances/{performance_id}")
    def get_performance(performance_id: str) -> dict[str, Any]:
        return performance_json(festival.performance(performance_id))

    @app.get("/api/now")
    def get_now(at: datetime | None = None) -> dict[str, Any]:
        moment = at or datetime.now()
        return {
            "at": moment.isoformat(timespec="minutes"),
            "now_playing": [performance_json(p) for p in festival.now_playing(moment)],
            "up_next": [performance_json(p) for p in festival.up_next(moment)],
        }

    @app.post("/api/artists", status_code=201)
    def post_artist(body: ArtistBody) -> dict[str, Any]:
        artist = Artist(body.name, body.bio, body.photo_url)
        festival.add_artist(artist)
        storage.save(festival)
        return artist_json(artist)

    @app.post("/api/performances", status_code=201)
    def post_performance(body: PerformanceBody) -> dict[str, Any]:
        performance = build(body)
        festival.add_performance(performance)
        storage.save(festival)
        return performance_json(performance)

    @app.put("/api/performances/{performance_id}")
    def put_performance(performance_id: str, body: PerformanceBody) -> dict[str, Any]:
        festival.performance(performance_id)
        performance = build(body)
        festival.replace_performance(performance_id, performance)
        storage.save(festival)
        return performance_json(performance)

    @app.delete("/api/performances/{performance_id}", status_code=204)
    def delete_performance(performance_id: str) -> Response:
        festival.remove_performance(performance_id)
        storage.save(festival)
        return Response(status_code=204)

    @app.post("/api/performances/{performance_id}/participants", status_code=201)
    def post_participant(performance_id: str, body: ParticipantBody) -> dict[str, Any]:
        workshop = festival.register(performance_id, body.name)
        storage.save(festival)
        return performance_json(workshop)

    app.mount("/admin", StaticFiles(directory=WEB / "admin", html=True), name="admin")
    app.mount("/", StaticFiles(directory=WEB / "public", html=True), name="public")
    return app


def venue_json(venue: Any) -> dict[str, Any]:
    return {
        "slug": venue.slug,
        "name": venue.name,
        "capacity": venue.capacity,
        "address": venue.address,
    }


def artist_json(artist: Artist) -> dict[str, Any]:
    return {
        "slug": artist.slug,
        "name": artist.name,
        "bio": artist.bio,
        "photo_url": artist.photo_url,
    }


def performance_json(performance: Performance) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": performance.id,
        "kind": performance.kind,
        "title": performance.title,
        "venue": performance.venue.slug,
        "venue_name": performance.venue.name,
        "start": performance.start.isoformat(timespec="minutes"),
        "end": performance.end.isoformat(timespec="minutes"),
        "duration_minutes": performance.duration_minutes,
        "festival_day": performance.festival_day.isoformat(),
        "description": performance.description,
        "summary": summary(performance),
        "capacity": performance.capacity,
        "artists": [{"slug": a.slug, "name": a.name} for a in performance.artists()],
    }
    if isinstance(performance, Solo):
        result["artist"] = performance.artist.slug
        result["min_age"] = performance.min_age
    elif isinstance(performance, Lineup):
        result["host"] = performance.host.slug
        result["acts"] = [act.slug for act in performance.acts]
    elif isinstance(performance, Workshop):
        result["teacher"] = performance.teacher.slug
        result["max_participants"] = performance.max_participants
        result["participants"] = performance.participants
        result["places_left"] = performance.places_left
    return result


def summary(performance: Performance) -> str:
    if isinstance(performance, Solo):
        return f"by {performance.artist.name}"
    if isinstance(performance, Lineup):
        acts = ", ".join(act.name for act in performance.acts)
        return f"hosted by {performance.host.name}, with {acts}"
    if isinstance(performance, Workshop):
        return (
            f"with {performance.teacher.name}, {performance.places_left} place(s) left"
        )
    return ""


app = create_app(JsonStorage(DATA_FILE))
