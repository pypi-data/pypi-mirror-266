"""ISO 3166 related types."""

from typing import NamedTuple


class Iso3166_1(NamedTuple):
    """ISO 3166-1 lightweight immutable entity."""

    # Country name, short form.
    short_name: str

    # Alphabetic 2 character code.
    alpha_2: str

    # Alphabetic 3 character code.
    alpha_3: str

    # Three-digit numeric code.
    num_3: str

    # Country name, long form .
    long_name: str

    # Sovereign country code.
    parent_code: str = ""

    def __str__(self) -> str:
        return f"ISO 3166-1 {self.alpha_2}"

    @property
    def is_independent(self):
        return self.parent_code == ""


class Iso3166_2(NamedTuple):
    """ISO 3166-2 lightweight immutable entity."""

    # Subdivision name.
    name: str

    # Subdivision code.
    code: str

    # Category.
    category: str

    # Language code.
    language_code: str

    # Parent code.
    parent_code: str = ""

    def __str__(self) -> str:
        return f"ISO 3166-2 {self.code}"
