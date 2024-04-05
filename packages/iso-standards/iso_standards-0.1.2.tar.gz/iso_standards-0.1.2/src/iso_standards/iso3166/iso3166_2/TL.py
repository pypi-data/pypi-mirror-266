"""ISO 3166-2 TL standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:TL
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "TL-AL": (
            Entity("Aileu", "TL-AL", "MUNICIPALITY", "pt", ""),
            Entity("Aileu", "TL-AL", "MUNICIPALITY", "", ""),
        ),
        "TL-AN": (
            Entity("Ainaro", "TL-AN", "MUNICIPALITY", "pt", ""),
            Entity("Ainaru", "TL-AN", "MUNICIPALITY", "", ""),
        ),
        "TL-BA": (
            Entity("Baucau", "TL-BA", "MUNICIPALITY", "pt", ""),
            Entity("Baukau", "TL-BA", "MUNICIPALITY", "", ""),
        ),
        "TL-BO": (
            Entity("Bobonaro", "TL-BO", "MUNICIPALITY", "pt", ""),
            Entity("Bobonaru", "TL-BO", "MUNICIPALITY", "", ""),
        ),
        "TL-CO": (
            Entity("Cova Lima", "TL-CO", "MUNICIPALITY", "pt", ""),
            Entity("Kovalima", "TL-CO", "MUNICIPALITY", "", ""),
        ),
        "TL-DI": (
            Entity("Díli", "TL-DI", "MUNICIPALITY", "pt", ""),
            Entity("Díli", "TL-DI", "MUNICIPALITY", "", ""),
        ),
        "TL-ER": (
            Entity("Ermera", "TL-ER", "MUNICIPALITY", "pt", ""),
            Entity("Ermera", "TL-ER", "MUNICIPALITY", "", ""),
        ),
        "TL-LA": (
            Entity("Lautein", "TL-LA", "MUNICIPALITY", "", ""),
            Entity("Lautém", "TL-LA", "MUNICIPALITY", "pt", ""),
        ),
        "TL-LI": (
            Entity("Likisá", "TL-LI", "MUNICIPALITY", "", ""),
            Entity("Liquiça", "TL-LI", "MUNICIPALITY", "pt", ""),
        ),
        "TL-MF": (
            Entity("Manufahi", "TL-MF", "MUNICIPALITY", "pt", ""),
            Entity("Manufahi", "TL-MF", "MUNICIPALITY", "", ""),
        ),
        "TL-MT": (
            Entity("Manatuto", "TL-MT", "MUNICIPALITY", "pt", ""),
            Entity("Manatutu", "TL-MT", "MUNICIPALITY", "", ""),
        ),
        "TL-OE": (
            Entity("Oekusi-Ambenu", "TL-OE", "SPECIAL ADMINISTRATIVE REGION", "", ""),
            Entity("Oé-Cusse Ambeno", "TL-OE", "SPECIAL ADMINISTRATIVE REGION", "pt", ""),
        ),
        "TL-VI": (
            Entity("Vikeke", "TL-VI", "MUNICIPALITY", "", ""),
            Entity("Viqueque", "TL-VI", "MUNICIPALITY", "pt", ""),
        ),
    }
