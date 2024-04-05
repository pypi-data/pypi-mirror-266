"""ISO 3166-2 YE standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:YE
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "YE-AB": (Entity("Abyan", "YE-AB", "GOVERNORATE", "ar", ""),),
        "YE-AD": (Entity("‘Adan", "YE-AD", "GOVERNORATE", "ar", ""),),
        "YE-AM": (Entity("‘Amrān", "YE-AM", "GOVERNORATE", "ar", ""),),
        "YE-BA": (Entity("Al Bayḑā’", "YE-BA", "GOVERNORATE", "ar", ""),),
        "YE-DA": (Entity("Aḑ Ḑāli‘", "YE-DA", "GOVERNORATE", "ar", ""),),
        "YE-DH": (Entity("Dhamār", "YE-DH", "GOVERNORATE", "ar", ""),),
        "YE-HD": (Entity("Ḩaḑramawt", "YE-HD", "GOVERNORATE", "ar", ""),),
        "YE-HJ": (Entity("Ḩajjah", "YE-HJ", "GOVERNORATE", "ar", ""),),
        "YE-HU": (Entity("Al Ḩudaydah", "YE-HU", "GOVERNORATE", "ar", ""),),
        "YE-IB": (Entity("Ibb", "YE-IB", "GOVERNORATE", "ar", ""),),
        "YE-JA": (Entity("Al Jawf", "YE-JA", "GOVERNORATE", "ar", ""),),
        "YE-LA": (Entity("Laḩij", "YE-LA", "GOVERNORATE", "ar", ""),),
        "YE-MA": (Entity("Ma’rib", "YE-MA", "GOVERNORATE", "ar", ""),),
        "YE-MR": (Entity("Al Mahrah", "YE-MR", "GOVERNORATE", "ar", ""),),
        "YE-MW": (Entity("Al Maḩwīt", "YE-MW", "GOVERNORATE", "ar", ""),),
        "YE-RA": (Entity("Raymah", "YE-RA", "GOVERNORATE", "ar", ""),),
        "YE-SA": (Entity("Amānat al ‘Āşimah", "YE-SA", "MUNICIPALITY", "ar", ""),),
        "YE-SD": (Entity("Şāʻdah", "YE-SD", "GOVERNORATE", "ar", ""),),
        "YE-SH": (Entity("Shabwah", "YE-SH", "GOVERNORATE", "ar", ""),),
        "YE-SN": (Entity("Şanʻā’", "YE-SN", "GOVERNORATE", "ar", ""),),
        "YE-SU": (Entity("Arkhabīl Suquţrá", "YE-SU", "GOVERNORATE", "ar", ""),),
        "YE-TA": (Entity("Tāʻizz", "YE-TA", "GOVERNORATE", "ar", ""),),
    }
