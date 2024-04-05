"""ISO 3166-2 SB standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SB
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SB-CE": (Entity("Central", "SB-CE", "PROVINCE", "en", ""),),
        "SB-CH": (Entity("Choiseul", "SB-CH", "PROVINCE", "en", ""),),
        "SB-CT": (Entity("Capital Territory", "SB-CT", "CAPITAL TERRITORY", "en", ""),),
        "SB-GU": (Entity("Guadalcanal", "SB-GU", "PROVINCE", "en", ""),),
        "SB-IS": (Entity("Isabel", "SB-IS", "PROVINCE", "en", ""),),
        "SB-MK": (Entity("Makira-Ulawa", "SB-MK", "PROVINCE", "en", ""),),
        "SB-ML": (Entity("Malaita", "SB-ML", "PROVINCE", "en", ""),),
        "SB-RB": (Entity("Rennell and Bellona", "SB-RB", "PROVINCE", "en", ""),),
        "SB-TE": (Entity("Temotu", "SB-TE", "PROVINCE", "en", ""),),
        "SB-WE": (Entity("Western", "SB-WE", "PROVINCE", "en", ""),),
    }
