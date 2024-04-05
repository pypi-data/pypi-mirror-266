"""ISO 3166-2 ZM standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:ZM
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "ZM-01": (Entity("Western", "ZM-01", "PROVINCE", "en", ""),),
        "ZM-02": (Entity("Central", "ZM-02", "PROVINCE", "en", ""),),
        "ZM-03": (Entity("Eastern", "ZM-03", "PROVINCE", "en", ""),),
        "ZM-04": (Entity("Luapula", "ZM-04", "PROVINCE", "en", ""),),
        "ZM-05": (Entity("Northern", "ZM-05", "PROVINCE", "en", ""),),
        "ZM-06": (Entity("North-Western", "ZM-06", "PROVINCE", "en", ""),),
        "ZM-07": (Entity("Southern", "ZM-07", "PROVINCE", "en", ""),),
        "ZM-08": (Entity("Copperbelt", "ZM-08", "PROVINCE", "en", ""),),
        "ZM-09": (Entity("Lusaka", "ZM-09", "PROVINCE", "en", ""),),
        "ZM-10": (Entity("Muchinga", "ZM-10", "PROVINCE", "en", ""),),
    }
