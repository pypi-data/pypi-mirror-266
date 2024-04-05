"""ISO 3166-2 SZ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SZ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SZ-HH": (
            Entity("Hhohho", "SZ-HH", "REGION", "en", ""),
            Entity("Hhohho", "SZ-HH", "REGION", "ss", ""),
        ),
        "SZ-LU": (
            Entity("Lubombo", "SZ-LU", "REGION", "en", ""),
            Entity("Lubombo", "SZ-LU", "REGION", "ss", ""),
        ),
        "SZ-MA": (
            Entity("Manzini", "SZ-MA", "REGION", "en", ""),
            Entity("Manzini", "SZ-MA", "REGION", "ss", ""),
        ),
        "SZ-SH": (
            Entity("Shiselweni", "SZ-SH", "REGION", "en", ""),
            Entity("Shiselweni", "SZ-SH", "REGION", "ss", ""),
        ),
    }
