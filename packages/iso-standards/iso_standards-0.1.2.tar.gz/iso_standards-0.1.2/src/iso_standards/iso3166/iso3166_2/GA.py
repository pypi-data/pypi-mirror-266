"""ISO 3166-2 GA standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:GA
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "GA-1": (Entity("Estuaire", "GA-1", "PROVINCE", "fr", ""),),
        "GA-2": (Entity("Haut-Ogooué", "GA-2", "PROVINCE", "fr", ""),),
        "GA-3": (Entity("Moyen-Ogooué", "GA-3", "PROVINCE", "fr", ""),),
        "GA-4": (Entity("Ngounié", "GA-4", "PROVINCE", "fr", ""),),
        "GA-5": (Entity("Nyanga", "GA-5", "PROVINCE", "fr", ""),),
        "GA-6": (Entity("Ogooué-Ivindo", "GA-6", "PROVINCE", "fr", ""),),
        "GA-7": (Entity("Ogooué-Lolo", "GA-7", "PROVINCE", "fr", ""),),
        "GA-8": (Entity("Ogooué-Maritime", "GA-8", "PROVINCE", "fr", ""),),
        "GA-9": (Entity("Woleu-Ntem", "GA-9", "PROVINCE", "fr", ""),),
    }
