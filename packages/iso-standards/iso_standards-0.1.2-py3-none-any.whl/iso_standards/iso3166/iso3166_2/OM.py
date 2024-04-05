"""ISO 3166-2 OM standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:OM
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "OM-BJ": (Entity("Janūb al Bāţinah", "OM-BJ", "GOVERNORATE", "ar", ""),),
        "OM-BS": (Entity("Shamāl al Bāţinah", "OM-BS", "GOVERNORATE", "ar", ""),),
        "OM-BU": (Entity("Al Buraymī", "OM-BU", "GOVERNORATE", "ar", ""),),
        "OM-DA": (Entity("Ad Dākhilīyah", "OM-DA", "GOVERNORATE", "ar", ""),),
        "OM-MA": (Entity("Masqaţ", "OM-MA", "GOVERNORATE", "ar", ""),),
        "OM-MU": (Entity("Musandam", "OM-MU", "GOVERNORATE", "ar", ""),),
        "OM-SJ": (Entity("Janūb ash Sharqīyah", "OM-SJ", "GOVERNORATE", "ar", ""),),
        "OM-SS": (Entity("Shamāl ash Sharqīyah", "OM-SS", "GOVERNORATE", "ar", ""),),
        "OM-WU": (Entity("Al Wusţá", "OM-WU", "GOVERNORATE", "ar", ""),),
        "OM-ZA": (Entity("Az̧ Z̧āhirah", "OM-ZA", "GOVERNORATE", "ar", ""),),
        "OM-ZU": (Entity("Z̧ufār", "OM-ZU", "GOVERNORATE", "ar", ""),),
    }
