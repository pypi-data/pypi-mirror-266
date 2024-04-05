"""ISO 3166-2 BH standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BH
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BH-13": (Entity("Al ‘Āşimah", "BH-13", "GOVERNORATE", "ar", ""),),
        "BH-14": (Entity("Al Janūbīyah", "BH-14", "GOVERNORATE", "ar", ""),),
        "BH-15": (Entity("Al Muḩarraq", "BH-15", "GOVERNORATE", "ar", ""),),
        "BH-17": (Entity("Ash Shamālīyah", "BH-17", "GOVERNORATE", "ar", ""),),
    }
