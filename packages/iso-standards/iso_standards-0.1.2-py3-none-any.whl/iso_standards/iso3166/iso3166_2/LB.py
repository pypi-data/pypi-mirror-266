"""ISO 3166-2 LB standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:LB
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "LB-AK": (
            Entity("Aakkâr", "LB-AK", "GOVERNORATE", "ar", ""),
            Entity("‘Akkār", "LB-AK", "GOVERNORATE", "ar", ""),
        ),
        "LB-AS": (
            Entity("Ash Shimāl", "LB-AS", "GOVERNORATE", "ar", ""),
            Entity("Liban-Nord", "LB-AS", "GOVERNORATE", "ar", ""),
        ),
        "LB-BA": (
            Entity("Bayrūt", "LB-BA", "GOVERNORATE", "ar", ""),
            Entity("Beyrouth", "LB-BA", "GOVERNORATE", "ar", ""),
        ),
        "LB-BH": (
            Entity("Baalbek-Hermel", "LB-BH", "GOVERNORATE", "ar", ""),
            Entity("B‘alabak-Al Hirmil", "LB-BH", "GOVERNORATE", "ar", ""),
        ),
        "LB-BI": (
            Entity("Al Biqā‘", "LB-BI", "GOVERNORATE", "ar", ""),
            Entity("Béqaa", "LB-BI", "GOVERNORATE", "ar", ""),
        ),
        "LB-JA": (
            Entity("Al Janūb", "LB-JA", "GOVERNORATE", "ar", ""),
            Entity("Liban-Sud", "LB-JA", "GOVERNORATE", "ar", ""),
        ),
        "LB-JL": (
            Entity("Jabal Lubnān", "LB-JL", "GOVERNORATE", "ar", ""),
            Entity("Mont-Liban", "LB-JL", "GOVERNORATE", "ar", ""),
        ),
        "LB-NA": (
            Entity("An Nabaţīyah", "LB-NA", "GOVERNORATE", "ar", ""),
            Entity("Nabatîyé", "LB-NA", "GOVERNORATE", "ar", ""),
        ),
    }
