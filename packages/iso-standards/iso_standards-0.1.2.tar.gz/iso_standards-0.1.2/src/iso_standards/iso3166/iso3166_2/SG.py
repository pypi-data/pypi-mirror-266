"""ISO 3166-2 SG standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SG
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SG-01": (Entity("Central Singapore", "SG-01", "DISTRICT", "en", ""),),
        "SG-02": (Entity("North East", "SG-02", "DISTRICT", "en", ""),),
        "SG-03": (Entity("North West", "SG-03", "DISTRICT", "en", ""),),
        "SG-04": (Entity("South East", "SG-04", "DISTRICT", "en", ""),),
        "SG-05": (Entity("South West", "SG-05", "DISTRICT", "en", ""),),
    }
