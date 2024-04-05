"""ISO 3166-2 UZ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:UZ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "UZ-AN": (Entity("Andijon", "UZ-AN", "REGION", "uz", ""),),
        "UZ-BU": (Entity("Buxoro", "UZ-BU", "REGION", "uz", ""),),
        "UZ-FA": (Entity("Farg‘ona", "UZ-FA", "REGION", "uz", ""),),
        "UZ-JI": (Entity("Jizzax", "UZ-JI", "REGION", "uz", ""),),
        "UZ-NG": (Entity("Namangan", "UZ-NG", "REGION", "uz", ""),),
        "UZ-NW": (Entity("Navoiy", "UZ-NW", "REGION", "uz", ""),),
        "UZ-QA": (Entity("Qashqadaryo", "UZ-QA", "REGION", "uz", ""),),
        "UZ-QR": (Entity("Qoraqalpog‘iston Respublikasi", "UZ-QR", "REPUBLIC", "uz", ""),),
        "UZ-SA": (Entity("Samarqand", "UZ-SA", "REGION", "uz", ""),),
        "UZ-SI": (Entity("Sirdaryo", "UZ-SI", "REGION", "uz", ""),),
        "UZ-SU": (Entity("Surxondaryo", "UZ-SU", "REGION", "uz", ""),),
        "UZ-TK": (Entity("Toshkent", "UZ-TK", "CITY", "uz", ""),),
        "UZ-TO": (Entity("Toshkent", "UZ-TO", "REGION", "uz", ""),),
        "UZ-XO": (Entity("Xorazm", "UZ-XO", "REGION", "uz", ""),),
    }
