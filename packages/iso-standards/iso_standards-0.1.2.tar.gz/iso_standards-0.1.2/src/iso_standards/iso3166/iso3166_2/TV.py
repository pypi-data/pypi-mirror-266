"""ISO 3166-2 TV standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:TV
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "TV-FUN": (Entity("Funafuti", "TV-FUN", "TOWN COUNCIL", "en", ""),),
        "TV-NIT": (Entity("Niutao", "TV-NIT", "ISLAND COUNCIL", "en", ""),),
        "TV-NKF": (Entity("Nukufetau", "TV-NKF", "ISLAND COUNCIL", "en", ""),),
        "TV-NKL": (Entity("Nukulaelae", "TV-NKL", "ISLAND COUNCIL", "en", ""),),
        "TV-NMA": (Entity("Nanumea", "TV-NMA", "ISLAND COUNCIL", "en", ""),),
        "TV-NMG": (Entity("Nanumaga", "TV-NMG", "ISLAND COUNCIL", "en", ""),),
        "TV-NUI": (Entity("Nui", "TV-NUI", "ISLAND COUNCIL", "en", ""),),
        "TV-VAI": (Entity("Vaitupu", "TV-VAI", "ISLAND COUNCIL", "en", ""),),
    }
