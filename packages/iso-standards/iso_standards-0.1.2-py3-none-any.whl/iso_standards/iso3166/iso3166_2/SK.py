"""ISO 3166-2 SK standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SK
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SK-BC": (Entity("Banskobystrický kraj", "SK-BC", "REGION", "sk", ""),),
        "SK-BL": (Entity("Bratislavský kraj", "SK-BL", "REGION", "sk", ""),),
        "SK-KI": (Entity("Košický kraj", "SK-KI", "REGION", "sk", ""),),
        "SK-NI": (Entity("Nitriansky kraj", "SK-NI", "REGION", "sk", ""),),
        "SK-PV": (Entity("Prešovský kraj", "SK-PV", "REGION", "sk", ""),),
        "SK-TA": (Entity("Trnavský kraj", "SK-TA", "REGION", "sk", ""),),
        "SK-TC": (Entity("Trenčiansky kraj", "SK-TC", "REGION", "sk", ""),),
        "SK-ZI": (Entity("Žilinský kraj", "SK-ZI", "REGION", "sk", ""),),
    }
