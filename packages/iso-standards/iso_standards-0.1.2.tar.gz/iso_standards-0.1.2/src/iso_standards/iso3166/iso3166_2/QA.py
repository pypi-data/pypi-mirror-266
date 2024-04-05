"""ISO 3166-2 QA standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:QA
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "QA-DA": (Entity("Ad Dawḩah", "QA-DA", "MUNICIPALITY", "ar", ""),),
        "QA-KH": (Entity("Al Khawr wa adh Dhakhīrah", "QA-KH", "MUNICIPALITY", "ar", ""),),
        "QA-MS": (Entity("Ash Shamāl", "QA-MS", "MUNICIPALITY", "ar", ""),),
        "QA-RA": (Entity("Ar Rayyān", "QA-RA", "MUNICIPALITY", "ar", ""),),
        "QA-SH": (Entity("Ash Shīḩānīyah", "QA-SH", "MUNICIPALITY", "ar", ""),),
        "QA-US": (Entity("Umm Şalāl", "QA-US", "MUNICIPALITY", "ar", ""),),
        "QA-WA": (Entity("Al Wakrah", "QA-WA", "MUNICIPALITY", "ar", ""),),
        "QA-ZA": (Entity("Az̧ Z̧a‘āyin", "QA-ZA", "MUNICIPALITY", "ar", ""),),
    }
