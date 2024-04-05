"""ISO 3166-2 SS standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SS
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SS-BN": (Entity("Northern Bahr el Ghazal", "SS-BN", "STATE", "en", ""),),
        "SS-BW": (Entity("Western Bahr el Ghazal", "SS-BW", "STATE", "en", ""),),
        "SS-EC": (Entity("Central Equatoria", "SS-EC", "STATE", "en", ""),),
        "SS-EE": (Entity("Eastern Equatoria", "SS-EE", "STATE", "en", ""),),
        "SS-EW": (Entity("Western Equatoria", "SS-EW", "STATE", "en", ""),),
        "SS-JG": (Entity("Jonglei", "SS-JG", "STATE", "en", ""),),
        "SS-LK": (Entity("Lakes", "SS-LK", "STATE", "en", ""),),
        "SS-NU": (Entity("Upper Nile", "SS-NU", "STATE", "en", ""),),
        "SS-UY": (Entity("Unity", "SS-UY", "STATE", "en", ""),),
        "SS-WR": (Entity("Warrap", "SS-WR", "STATE", "en", ""),),
    }
