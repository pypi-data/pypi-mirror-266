"""ISO 3166-2 SO standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SO
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SO-AW": (Entity("Awdal", "SO-AW", "REGION", "so", ""),),
        "SO-BK": (Entity("Bakool", "SO-BK", "REGION", "so", ""),),
        "SO-BN": (Entity("Banaadir", "SO-BN", "REGION", "so", ""),),
        "SO-BR": (Entity("Bari", "SO-BR", "REGION", "so", ""),),
        "SO-BY": (Entity("Bay", "SO-BY", "REGION", "so", ""),),
        "SO-GA": (Entity("Galguduud", "SO-GA", "REGION", "so", ""),),
        "SO-GE": (Entity("Gedo", "SO-GE", "REGION", "so", ""),),
        "SO-HI": (Entity("Hiiraan", "SO-HI", "REGION", "so", ""),),
        "SO-JD": (Entity("Jubbada Dhexe", "SO-JD", "REGION", "so", ""),),
        "SO-JH": (Entity("Jubbada Hoose", "SO-JH", "REGION", "so", ""),),
        "SO-MU": (Entity("Mudug", "SO-MU", "REGION", "so", ""),),
        "SO-NU": (Entity("Nugaal", "SO-NU", "REGION", "so", ""),),
        "SO-SA": (Entity("Sanaag", "SO-SA", "REGION", "so", ""),),
        "SO-SD": (Entity("Shabeellaha Dhexe", "SO-SD", "REGION", "so", ""),),
        "SO-SH": (Entity("Shabeellaha Hoose", "SO-SH", "REGION", "so", ""),),
        "SO-SO": (Entity("Sool", "SO-SO", "REGION", "so", ""),),
        "SO-TO": (Entity("Togdheer", "SO-TO", "REGION", "so", ""),),
        "SO-WO": (Entity("Woqooyi Galbeed", "SO-WO", "REGION", "so", ""),),
    }
