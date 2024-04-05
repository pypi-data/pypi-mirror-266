"""ISO 3166-2 BW standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BW
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BW-CE": (Entity("Central", "BW-CE", "DISTRICT", "en", ""),),
        "BW-CH": (Entity("Chobe", "BW-CH", "DISTRICT", "en", ""),),
        "BW-FR": (Entity("Francistown", "BW-FR", "CITY", "en", ""),),
        "BW-GA": (Entity("Gaborone", "BW-GA", "CITY", "en", ""),),
        "BW-GH": (Entity("Ghanzi", "BW-GH", "DISTRICT", "en", ""),),
        "BW-JW": (Entity("Jwaneng", "BW-JW", "TOWN", "en", ""),),
        "BW-KG": (Entity("Kgalagadi", "BW-KG", "DISTRICT", "en", ""),),
        "BW-KL": (Entity("Kgatleng", "BW-KL", "DISTRICT", "en", ""),),
        "BW-KW": (Entity("Kweneng", "BW-KW", "DISTRICT", "en", ""),),
        "BW-LO": (Entity("Lobatse", "BW-LO", "TOWN", "en", ""),),
        "BW-NE": (Entity("North East", "BW-NE", "DISTRICT", "en", ""),),
        "BW-NW": (Entity("North West", "BW-NW", "DISTRICT", "en", ""),),
        "BW-SE": (Entity("South East", "BW-SE", "DISTRICT", "en", ""),),
        "BW-SO": (Entity("Southern", "BW-SO", "DISTRICT", "en", ""),),
        "BW-SP": (Entity("Selibe Phikwe", "BW-SP", "TOWN", "en", ""),),
        "BW-ST": (Entity("Sowa Town", "BW-ST", "TOWN", "en", ""),),
    }
