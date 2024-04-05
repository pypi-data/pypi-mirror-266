"""ISO 3166-2 KW standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:KW
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "KW-AH": (Entity("Al Aḩmadī", "KW-AH", "GOVERNORATE", "ar", ""),),
        "KW-FA": (Entity("Al Farwānīyah", "KW-FA", "GOVERNORATE", "ar", ""),),
        "KW-HA": (Entity("Ḩawallī", "KW-HA", "GOVERNORATE", "ar", ""),),
        "KW-JA": (Entity("Al Jahrā’", "KW-JA", "GOVERNORATE", "ar", ""),),
        "KW-KU": (Entity("Al ‘Āşimah", "KW-KU", "GOVERNORATE", "ar", ""),),
        "KW-MU": (Entity("Mubārak al Kabīr", "KW-MU", "GOVERNORATE", "ar", ""),),
    }
