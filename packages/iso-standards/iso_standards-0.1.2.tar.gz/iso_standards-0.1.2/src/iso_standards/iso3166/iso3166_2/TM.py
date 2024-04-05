"""ISO 3166-2 TM standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:TM
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "TM-A": (Entity("Ahal", "TM-A", "REGION", "tk", ""),),
        "TM-B": (Entity("Balkan", "TM-B", "REGION", "tk", ""),),
        "TM-D": (Entity("Daşoguz", "TM-D", "REGION", "tk", ""),),
        "TM-L": (Entity("Lebap", "TM-L", "REGION", "tk", ""),),
        "TM-M": (Entity("Mary", "TM-M", "REGION", "tk", ""),),
        "TM-S": (Entity("Aşgabat", "TM-S", "CITY", "tk", ""),),
    }
