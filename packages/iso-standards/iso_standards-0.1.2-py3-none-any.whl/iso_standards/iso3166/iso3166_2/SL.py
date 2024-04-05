"""ISO 3166-2 SL standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SL
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SL-E": (Entity("Eastern", "SL-E", "PROVINCE", "en", ""),),
        "SL-N": (Entity("Northern", "SL-N", "PROVINCE", "en", ""),),
        "SL-NW": (Entity("North Western", "SL-NW", "PROVINCE", "en", ""),),
        "SL-S": (Entity("Southern", "SL-S", "PROVINCE", "en", ""),),
        "SL-W": (Entity("Western Area", "SL-W", "AREA", "en", ""),),
    }
