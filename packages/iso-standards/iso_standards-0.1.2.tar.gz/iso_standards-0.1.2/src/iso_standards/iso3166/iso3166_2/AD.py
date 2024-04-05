"""ISO 3166-2 AD standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:AD
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "AD-02": (Entity("Canillo", "AD-02", "PARISH", "ca", ""),),
        "AD-03": (Entity("Encamp", "AD-03", "PARISH", "ca", ""),),
        "AD-04": (Entity("La Massana", "AD-04", "PARISH", "ca", ""),),
        "AD-05": (Entity("Ordino", "AD-05", "PARISH", "ca", ""),),
        "AD-06": (Entity("Sant Julià de Lòria", "AD-06", "PARISH", "ca", ""),),
        "AD-07": (Entity("Andorra la Vella", "AD-07", "PARISH", "ca", ""),),
        "AD-08": (Entity("Escaldes-Engordany", "AD-08", "PARISH", "ca", ""),),
    }
