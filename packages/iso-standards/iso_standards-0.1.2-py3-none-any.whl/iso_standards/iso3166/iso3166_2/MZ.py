"""ISO 3166-2 MZ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:MZ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "MZ-A": (Entity("Niassa", "MZ-A", "PROVINCE", "pt", ""),),
        "MZ-B": (Entity("Manica", "MZ-B", "PROVINCE", "pt", ""),),
        "MZ-G": (Entity("Gaza", "MZ-G", "PROVINCE", "pt", ""),),
        "MZ-I": (Entity("Inhambane", "MZ-I", "PROVINCE", "pt", ""),),
        "MZ-L": (Entity("Maputo", "MZ-L", "PROVINCE", "pt", ""),),
        "MZ-MPM": (Entity("Maputo", "MZ-MPM", "CITY", "pt", ""),),
        "MZ-N": (Entity("Nampula", "MZ-N", "PROVINCE", "pt", ""),),
        "MZ-P": (Entity("Cabo Delgado", "MZ-P", "PROVINCE", "pt", ""),),
        "MZ-Q": (Entity("Zambézia", "MZ-Q", "PROVINCE", "pt", ""),),
        "MZ-S": (Entity("Sofala", "MZ-S", "PROVINCE", "pt", ""),),
        "MZ-T": (Entity("Tete", "MZ-T", "PROVINCE", "pt", ""),),
    }
