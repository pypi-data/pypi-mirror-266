"""ISO 3166-2 BO standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BO
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BO-B": (Entity("El Beni", "BO-B", "DEPARTMENT", "es", ""),),
        "BO-C": (Entity("Cochabamba", "BO-C", "DEPARTMENT", "es", ""),),
        "BO-H": (Entity("Chuquisaca", "BO-H", "DEPARTMENT", "es", ""),),
        "BO-L": (Entity("La Paz", "BO-L", "DEPARTMENT", "es", ""),),
        "BO-N": (Entity("Pando", "BO-N", "DEPARTMENT", "es", ""),),
        "BO-O": (Entity("Oruro", "BO-O", "DEPARTMENT", "es", ""),),
        "BO-P": (Entity("Potosí", "BO-P", "DEPARTMENT", "es", ""),),
        "BO-S": (Entity("Santa Cruz", "BO-S", "DEPARTMENT", "es", ""),),
        "BO-T": (Entity("Tarija", "BO-T", "DEPARTMENT", "es", ""),),
    }
