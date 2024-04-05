"""ISO 3166-2 BB standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BB
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BB-01": (Entity("Christ Church", "BB-01", "PARISH", "en", ""),),
        "BB-02": (Entity("Saint Andrew", "BB-02", "PARISH", "en", ""),),
        "BB-03": (Entity("Saint George", "BB-03", "PARISH", "en", ""),),
        "BB-04": (Entity("Saint James", "BB-04", "PARISH", "en", ""),),
        "BB-05": (Entity("Saint John", "BB-05", "PARISH", "en", ""),),
        "BB-06": (Entity("Saint Joseph", "BB-06", "PARISH", "en", ""),),
        "BB-07": (Entity("Saint Lucy", "BB-07", "PARISH", "en", ""),),
        "BB-08": (Entity("Saint Michael", "BB-08", "PARISH", "en", ""),),
        "BB-09": (Entity("Saint Peter", "BB-09", "PARISH", "en", ""),),
        "BB-10": (Entity("Saint Philip", "BB-10", "PARISH", "en", ""),),
        "BB-11": (Entity("Saint Thomas", "BB-11", "PARISH", "en", ""),),
    }
