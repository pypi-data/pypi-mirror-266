"""ISO 3166-2 GE standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:GE
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "GE-AB": (Entity("Abkhazia", "GE-AB", "AUTONOMOUS REPUBLIC", "ka", ""),),
        "GE-AJ": (Entity("Ajaria", "GE-AJ", "AUTONOMOUS REPUBLIC", "ka", ""),),
        "GE-GU": (Entity("Guria", "GE-GU", "REGION", "ka", ""),),
        "GE-IM": (Entity("Imereti", "GE-IM", "REGION", "ka", ""),),
        "GE-KA": (Entity("K'akheti", "GE-KA", "REGION", "ka", ""),),
        "GE-KK": (Entity("Kvemo Kartli", "GE-KK", "REGION", "ka", ""),),
        "GE-MM": (Entity("Mtskheta-Mtianeti", "GE-MM", "REGION", "ka", ""),),
        "GE-RL": (Entity("Rach'a-Lechkhumi-Kvemo Svaneti", "GE-RL", "REGION", "ka", ""),),
        "GE-SJ": (Entity("Samtskhe-Javakheti", "GE-SJ", "REGION", "ka", ""),),
        "GE-SK": (Entity("Shida Kartli", "GE-SK", "REGION", "ka", ""),),
        "GE-SZ": (Entity("Samegrelo-Zemo Svaneti", "GE-SZ", "REGION", "ka", ""),),
        "GE-TB": (Entity("Tbilisi", "GE-TB", "CITY", "ka", ""),),
    }
