"""ISO 3166-2 NL standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:NL
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "NL-AW": (Entity("Aruba", "NL-AW", "COUNTRY", "nl", ""),),
        "NL-BQ1": (Entity("Bonaire", "NL-BQ1", "SPECIAL MUNICIPALITY", "nl", ""),),
        "NL-BQ2": (Entity("Saba", "NL-BQ2", "SPECIAL MUNICIPALITY", "nl", ""),),
        "NL-BQ3": (Entity("Sint Eustatius", "NL-BQ3", "SPECIAL MUNICIPALITY", "nl", ""),),
        "NL-CW": (Entity("Curaçao", "NL-CW", "COUNTRY", "nl", ""),),
        "NL-DR": (Entity("Drenthe", "NL-DR", "PROVINCE", "nl", ""),),
        "NL-FL": (Entity("Flevoland", "NL-FL", "PROVINCE", "nl", ""),),
        "NL-FR": (Entity("Fryslân", "NL-FR", "PROVINCE", "fy", ""),),
        "NL-GE": (Entity("Gelderland", "NL-GE", "PROVINCE", "nl", ""),),
        "NL-GR": (Entity("Groningen", "NL-GR", "PROVINCE", "nl", ""),),
        "NL-LI": (Entity("Limburg", "NL-LI", "PROVINCE", "nl", ""),),
        "NL-NB": (Entity("Noord-Brabant", "NL-NB", "PROVINCE", "nl", ""),),
        "NL-NH": (Entity("Noord-Holland", "NL-NH", "PROVINCE", "nl", ""),),
        "NL-OV": (Entity("Overijssel", "NL-OV", "PROVINCE", "nl", ""),),
        "NL-SX": (Entity("Sint Maarten", "NL-SX", "COUNTRY", "nl", ""),),
        "NL-UT": (Entity("Utrecht", "NL-UT", "PROVINCE", "nl", ""),),
        "NL-ZE": (Entity("Zeeland", "NL-ZE", "PROVINCE", "nl", ""),),
        "NL-ZH": (Entity("Zuid-Holland", "NL-ZH", "PROVINCE", "nl", ""),),
    }
