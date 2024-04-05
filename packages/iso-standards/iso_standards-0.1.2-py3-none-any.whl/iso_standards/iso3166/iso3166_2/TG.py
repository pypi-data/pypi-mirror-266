"""ISO 3166-2 TG standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:TG
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "TG-C": (Entity("Centrale", "TG-C", "REGION", "fr", ""),),
        "TG-K": (Entity("Kara", "TG-K", "REGION", "fr", ""),),
        "TG-M": (Entity("Maritime", "TG-M", "REGION", "fr", ""),),
        "TG-P": (Entity("Plateaux", "TG-P", "REGION", "fr", ""),),
        "TG-S": (Entity("Savanes", "TG-S", "REGION", "fr", ""),),
    }
