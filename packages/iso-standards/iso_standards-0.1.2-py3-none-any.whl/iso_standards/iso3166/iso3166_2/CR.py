"""ISO 3166-2 CR standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CR
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CR-A": (Entity("Alajuela", "CR-A", "PROVINCE", "es", ""),),
        "CR-C": (Entity("Cartago", "CR-C", "PROVINCE", "es", ""),),
        "CR-G": (Entity("Guanacaste", "CR-G", "PROVINCE", "es", ""),),
        "CR-H": (Entity("Heredia", "CR-H", "PROVINCE", "es", ""),),
        "CR-L": (Entity("Limón", "CR-L", "PROVINCE", "es", ""),),
        "CR-P": (Entity("Puntarenas", "CR-P", "PROVINCE", "es", ""),),
        "CR-SJ": (Entity("San José", "CR-SJ", "PROVINCE", "es", ""),),
    }
