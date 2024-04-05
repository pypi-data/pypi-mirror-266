"""ISO 3166-2 LR standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:LR
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "LR-BG": (Entity("Bong", "LR-BG", "COUNTY", "en", ""),),
        "LR-BM": (Entity("Bomi", "LR-BM", "COUNTY", "en", ""),),
        "LR-CM": (Entity("Grand Cape Mount", "LR-CM", "COUNTY", "en", ""),),
        "LR-GB": (Entity("Grand Bassa", "LR-GB", "COUNTY", "en", ""),),
        "LR-GG": (Entity("Grand Gedeh", "LR-GG", "COUNTY", "en", ""),),
        "LR-GK": (Entity("Grand Kru", "LR-GK", "COUNTY", "en", ""),),
        "LR-GP": (Entity("Gbarpolu", "LR-GP", "COUNTY", "en", ""),),
        "LR-LO": (Entity("Lofa", "LR-LO", "COUNTY", "en", ""),),
        "LR-MG": (Entity("Margibi", "LR-MG", "COUNTY", "en", ""),),
        "LR-MO": (Entity("Montserrado", "LR-MO", "COUNTY", "en", ""),),
        "LR-MY": (Entity("Maryland", "LR-MY", "COUNTY", "en", ""),),
        "LR-NI": (Entity("Nimba", "LR-NI", "COUNTY", "en", ""),),
        "LR-RG": (Entity("River Gee", "LR-RG", "COUNTY", "en", ""),),
        "LR-RI": (Entity("River Cess", "LR-RI", "COUNTY", "en", ""),),
        "LR-SI": (Entity("Sinoe", "LR-SI", "COUNTY", "en", ""),),
    }
