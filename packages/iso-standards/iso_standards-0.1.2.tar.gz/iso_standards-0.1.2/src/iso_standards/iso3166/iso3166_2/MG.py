"""ISO 3166-2 MG standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:MG
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "MG-A": (Entity("Toamasina", "MG-A", "PROVINCE", "mg", ""),),
        "MG-D": (Entity("Antsiranana", "MG-D", "PROVINCE", "mg", ""),),
        "MG-F": (Entity("Fianarantsoa", "MG-F", "PROVINCE", "mg", ""),),
        "MG-M": (Entity("Mahajanga", "MG-M", "PROVINCE", "mg", ""),),
        "MG-T": (Entity("Antananarivo", "MG-T", "PROVINCE", "mg", ""),),
        "MG-U": (Entity("Toliara", "MG-U", "PROVINCE", "mg", ""),),
    }
