"""ISO 3166-2 ER standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:ER
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "ER-AN": (
            Entity("Ansabā", "ER-AN", "REGION", "ar", ""),
            Entity("‘Anseba", "ER-AN", "REGION", "ti", ""),
        ),
        "ER-DK": (
            Entity("Debubawi K’eyyĭḥ Baḥri", "ER-DK", "REGION", "ti", ""),
            Entity("Janūbī al Baḩrī al Aḩmar", "ER-DK", "REGION", "ar", ""),
        ),
        "ER-DU": (
            Entity("Al Janūbī", "ER-DU", "REGION", "ar", ""),
            Entity("Debub", "ER-DU", "REGION", "ti", ""),
        ),
        "ER-GB": (
            Entity("Gash-Barka", "ER-GB", "REGION", "ti", ""),
            Entity("Qāsh-Barkah", "ER-GB", "REGION", "ar", ""),
        ),
        "ER-MA": (
            Entity("Al Awsaţ", "ER-MA", "REGION", "ar", ""),
            Entity("Ma’ĭkel", "ER-MA", "REGION", "ti", ""),
        ),
        "ER-SK": (
            Entity("Semienawi K’eyyĭḥ Baḥri", "ER-SK", "REGION", "ti", ""),
            Entity("Shimālī al Baḩrī al Aḩmar", "ER-SK", "REGION", "ar", ""),
        ),
    }
