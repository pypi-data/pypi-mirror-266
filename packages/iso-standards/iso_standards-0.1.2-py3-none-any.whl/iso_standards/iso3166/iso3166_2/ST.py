"""ISO 3166-2 ST standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:ST
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "ST-01": (Entity("Água Grande", "ST-01", "DISTRICT", "pt", ""),),
        "ST-02": (Entity("Cantagalo", "ST-02", "DISTRICT", "pt", ""),),
        "ST-03": (Entity("Caué", "ST-03", "DISTRICT", "pt", ""),),
        "ST-04": (Entity("Lembá", "ST-04", "DISTRICT", "pt", ""),),
        "ST-05": (Entity("Lobata", "ST-05", "DISTRICT", "pt", ""),),
        "ST-06": (Entity("Mé-Zóchi", "ST-06", "DISTRICT", "pt", ""),),
        "ST-P": (Entity("Príncipe", "ST-P", "AUTONOMOUS REGION", "pt", ""),),
    }
