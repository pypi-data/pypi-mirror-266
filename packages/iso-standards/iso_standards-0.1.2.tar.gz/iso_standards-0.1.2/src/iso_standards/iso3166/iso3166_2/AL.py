"""ISO 3166-2 AL standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:AL
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "AL-01": (Entity("Berat", "AL-01", "COUNTY", "sq", ""),),
        "AL-02": (Entity("Durrës", "AL-02", "COUNTY", "sq", ""),),
        "AL-03": (Entity("Elbasan", "AL-03", "COUNTY", "sq", ""),),
        "AL-04": (Entity("Fier", "AL-04", "COUNTY", "sq", ""),),
        "AL-05": (Entity("Gjirokastër", "AL-05", "COUNTY", "sq", ""),),
        "AL-06": (Entity("Korçë", "AL-06", "COUNTY", "sq", ""),),
        "AL-07": (Entity("Kukës", "AL-07", "COUNTY", "sq", ""),),
        "AL-08": (Entity("Lezhë", "AL-08", "COUNTY", "sq", ""),),
        "AL-09": (Entity("Dibër", "AL-09", "COUNTY", "sq", ""),),
        "AL-10": (Entity("Shkodër", "AL-10", "COUNTY", "sq", ""),),
        "AL-11": (Entity("Tiranë", "AL-11", "COUNTY", "sq", ""),),
        "AL-12": (Entity("Vlorë", "AL-12", "COUNTY", "sq", ""),),
    }
