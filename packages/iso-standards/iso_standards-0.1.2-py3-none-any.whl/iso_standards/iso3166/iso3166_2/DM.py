"""ISO 3166-2 DM standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:DM
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "DM-02": (Entity("Saint Andrew", "DM-02", "PARISH", "en", ""),),
        "DM-03": (Entity("Saint David", "DM-03", "PARISH", "en", ""),),
        "DM-04": (Entity("Saint George", "DM-04", "PARISH", "en", ""),),
        "DM-05": (Entity("Saint John", "DM-05", "PARISH", "en", ""),),
        "DM-06": (Entity("Saint Joseph", "DM-06", "PARISH", "en", ""),),
        "DM-07": (Entity("Saint Luke", "DM-07", "PARISH", "en", ""),),
        "DM-08": (Entity("Saint Mark", "DM-08", "PARISH", "en", ""),),
        "DM-09": (Entity("Saint Patrick", "DM-09", "PARISH", "en", ""),),
        "DM-10": (Entity("Saint Paul", "DM-10", "PARISH", "en", ""),),
        "DM-11": (Entity("Saint Peter", "DM-11", "PARISH", "en", ""),),
    }
