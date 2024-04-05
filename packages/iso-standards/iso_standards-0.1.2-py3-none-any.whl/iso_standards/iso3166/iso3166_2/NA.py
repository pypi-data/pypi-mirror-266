"""ISO 3166-2 NA standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:NA
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "NA-CA": (Entity("Zambezi", "NA-CA", "REGION", "en", ""),),
        "NA-ER": (Entity("Erongo", "NA-ER", "REGION", "en", ""),),
        "NA-HA": (Entity("Hardap", "NA-HA", "REGION", "en", ""),),
        "NA-KA": (Entity("//Karas", "NA-KA", "REGION", "en", ""),),
        "NA-KE": (Entity("Kavango East", "NA-KE", "REGION", "en", ""),),
        "NA-KH": (Entity("Khomas", "NA-KH", "REGION", "en", ""),),
        "NA-KU": (Entity("Kunene", "NA-KU", "REGION", "en", ""),),
        "NA-KW": (Entity("Kavango West", "NA-KW", "REGION", "en", ""),),
        "NA-OD": (Entity("Otjozondjupa", "NA-OD", "REGION", "en", ""),),
        "NA-OH": (Entity("Omaheke", "NA-OH", "REGION", "en", ""),),
        "NA-ON": (Entity("Oshana", "NA-ON", "REGION", "en", ""),),
        "NA-OS": (Entity("Omusati", "NA-OS", "REGION", "en", ""),),
        "NA-OT": (Entity("Oshikoto", "NA-OT", "REGION", "en", ""),),
        "NA-OW": (Entity("Ohangwena", "NA-OW", "REGION", "en", ""),),
    }
