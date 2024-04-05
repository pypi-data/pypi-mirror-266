"""ISO 3166-2 BJ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BJ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BJ-AK": (Entity("Atacora", "BJ-AK", "DEPARTMENT", "fr", ""),),
        "BJ-AL": (Entity("Alibori", "BJ-AL", "DEPARTMENT", "fr", ""),),
        "BJ-AQ": (Entity("Atlantique", "BJ-AQ", "DEPARTMENT", "fr", ""),),
        "BJ-BO": (Entity("Borgou", "BJ-BO", "DEPARTMENT", "fr", ""),),
        "BJ-CO": (Entity("Collines", "BJ-CO", "DEPARTMENT", "fr", ""),),
        "BJ-DO": (Entity("Donga", "BJ-DO", "DEPARTMENT", "fr", ""),),
        "BJ-KO": (Entity("Couffo", "BJ-KO", "DEPARTMENT", "fr", ""),),
        "BJ-LI": (Entity("Littoral", "BJ-LI", "DEPARTMENT", "fr", ""),),
        "BJ-MO": (Entity("Mono", "BJ-MO", "DEPARTMENT", "fr", ""),),
        "BJ-OU": (Entity("Ouémé", "BJ-OU", "DEPARTMENT", "fr", ""),),
        "BJ-PL": (Entity("Plateau", "BJ-PL", "DEPARTMENT", "fr", ""),),
        "BJ-ZO": (Entity("Zou", "BJ-ZO", "DEPARTMENT", "fr", ""),),
    }
