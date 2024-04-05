"""ISO 3166-2 DK standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:DK
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "DK-81": (Entity("Nordjylland", "DK-81", "REGION", "da", ""),),
        "DK-82": (Entity("Midtjylland", "DK-82", "REGION", "da", ""),),
        "DK-83": (Entity("Syddanmark", "DK-83", "REGION", "da", ""),),
        "DK-84": (Entity("Hovedstaden", "DK-84", "REGION", "da", ""),),
        "DK-85": (Entity("Sjælland", "DK-85", "REGION", "da", ""),),
    }
