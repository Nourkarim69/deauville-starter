"""Une salle du festival."""

from festival.errors import InvalidValueError
from festival.text import clean_name, slugify


class Venue:

    def __init__(self, name: str, capacity: int, address: str) -> None:
        self._name = clean_name(name, "venue name")
        self._slug = slugify(self._name)
        if not self._slug:
            raise InvalidValueError(f"The venue name {name!r} has no letter or digit.")
        if capacity < 1:
            raise InvalidValueError(
                f"{self._name} must have at least 1 seat, not {capacity}."
            )
        self._capacity = capacity
        self._address = address.strip()

    @property
    def name(self) -> str:
        return self._name

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def address(self) -> str:
        return self._address

    def __repr__(self) -> str:
        return f"Venue({self._name!r}, {self._capacity}, {self._address!r})"