"""ISO 3166-2 CD standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CD
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CD-BC": (Entity("Kongo Central", "CD-BC", "PROVINCE", "fr", ""),),
        "CD-BU": (Entity("Bas-Uélé", "CD-BU", "PROVINCE", "fr", ""),),
        "CD-EQ": (Entity("Équateur", "CD-EQ", "PROVINCE", "fr", ""),),
        "CD-HK": (Entity("Haut-Katanga", "CD-HK", "PROVINCE", "fr", ""),),
        "CD-HL": (Entity("Haut-Lomami", "CD-HL", "PROVINCE", "fr", ""),),
        "CD-HU": (Entity("Haut-Uélé", "CD-HU", "PROVINCE", "fr", ""),),
        "CD-IT": (Entity("Ituri", "CD-IT", "PROVINCE", "fr", ""),),
        "CD-KC": (Entity("Kasaï Central", "CD-KC", "PROVINCE", "fr", ""),),
        "CD-KE": (Entity("Kasaï Oriental", "CD-KE", "PROVINCE", "fr", ""),),
        "CD-KG": (Entity("Kwango", "CD-KG", "PROVINCE", "fr", ""),),
        "CD-KL": (Entity("Kwilu", "CD-KL", "PROVINCE", "fr", ""),),
        "CD-KN": (Entity("Kinshasa", "CD-KN", "CITY", "fr", ""),),
        "CD-KS": (Entity("Kasaï", "CD-KS", "PROVINCE", "fr", ""),),
        "CD-LO": (Entity("Lomami", "CD-LO", "PROVINCE", "fr", ""),),
        "CD-LU": (Entity("Lualaba", "CD-LU", "PROVINCE", "fr", ""),),
        "CD-MA": (Entity("Maniema", "CD-MA", "PROVINCE", "fr", ""),),
        "CD-MN": (Entity("Mai-Ndombe", "CD-MN", "PROVINCE", "fr", ""),),
        "CD-MO": (Entity("Mongala", "CD-MO", "PROVINCE", "fr", ""),),
        "CD-NK": (Entity("Nord-Kivu", "CD-NK", "PROVINCE", "fr", ""),),
        "CD-NU": (Entity("Nord-Ubangi", "CD-NU", "PROVINCE", "fr", ""),),
        "CD-SA": (Entity("Sankuru", "CD-SA", "PROVINCE", "fr", ""),),
        "CD-SK": (Entity("Sud-Kivu", "CD-SK", "PROVINCE", "fr", ""),),
        "CD-SU": (Entity("Sud-Ubangi", "CD-SU", "PROVINCE", "fr", ""),),
        "CD-TA": (Entity("Tanganyika", "CD-TA", "PROVINCE", "fr", ""),),
        "CD-TO": (Entity("Tshopo", "CD-TO", "PROVINCE", "fr", ""),),
        "CD-TU": (Entity("Tshuapa", "CD-TU", "PROVINCE", "fr", ""),),
    }
