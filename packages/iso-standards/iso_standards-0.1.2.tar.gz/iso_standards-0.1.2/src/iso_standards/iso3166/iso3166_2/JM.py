"""ISO 3166-2 JM standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:JM
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "JM-01": (Entity("Kingston", "JM-01", "PARISH", "en", ""),),
        "JM-02": (Entity("Saint Andrew", "JM-02", "PARISH", "en", ""),),
        "JM-03": (Entity("Saint Thomas", "JM-03", "PARISH", "en", ""),),
        "JM-04": (Entity("Portland", "JM-04", "PARISH", "en", ""),),
        "JM-05": (Entity("Saint Mary", "JM-05", "PARISH", "en", ""),),
        "JM-06": (Entity("Saint Ann", "JM-06", "PARISH", "en", ""),),
        "JM-07": (Entity("Trelawny", "JM-07", "PARISH", "en", ""),),
        "JM-08": (Entity("Saint James", "JM-08", "PARISH", "en", ""),),
        "JM-09": (Entity("Hanover", "JM-09", "PARISH", "en", ""),),
        "JM-10": (Entity("Westmoreland", "JM-10", "PARISH", "en", ""),),
        "JM-11": (Entity("Saint Elizabeth", "JM-11", "PARISH", "en", ""),),
        "JM-12": (Entity("Manchester", "JM-12", "PARISH", "en", ""),),
        "JM-13": (Entity("Clarendon", "JM-13", "PARISH", "en", ""),),
        "JM-14": (Entity("Saint Catherine", "JM-14", "PARISH", "en", ""),),
    }
