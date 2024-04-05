"""ISO 3166-2 KI standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:KI
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "KI-G": (
            Entity("Gilbert Islands", "KI-G", "GROUP OF ISLANDS (20 INHABITED ISLANDS)", "en", ""),
        ),
        "KI-L": (
            Entity("Line Islands", "KI-L", "GROUP OF ISLANDS (20 INHABITED ISLANDS)", "en", ""),
        ),
        "KI-P": (
            Entity("Phoenix Islands", "KI-P", "GROUP OF ISLANDS (20 INHABITED ISLANDS)", "en", ""),
        ),
    }
