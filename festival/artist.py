"""Un artiste du festival."""

from festival.errors import InvalidValueError
from festival.text import clean_name, slugify


class Artist:
    """Un artiste : un nom, une bio et une photo (ces deux-là peuvent être vides)."""

    def __init__(self, name: str, bio: str = "", photo_url: str = "") -> None:
        self._name = clean_name(name, "artist name")
        self._slug = slugify(self._name)
        if not self._slug:
            raise InvalidValueError(f"The artist name {name!r} has no letter or digit.")
        self._bio = bio.strip()
        self._photo_url = photo_url.strip()

    @property
    def name(self) -> str:
        return self._name

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def bio(self) -> str:
        return self._bio

    @property
    def photo_url(self) -> str:
        return self._photo_url

    def __repr__(self) -> str:
        return f"Artist({self._name!r})"