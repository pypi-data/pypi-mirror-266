"""ISO 3166-2 BQ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BQ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BQ-BO": (
            Entity("Bonaire", "BQ-BO", "SPECIAL MUNICIPALITY", "en", ""),
            Entity("Bonaire", "BQ-BO", "SPECIAL MUNICIPALITY", "nl", ""),
            Entity("Boneiru", "BQ-BO", "SPECIAL MUNICIPALITY", "", ""),
        ),
        "BQ-SA": (
            Entity("Saba", "BQ-SA", "SPECIAL MUNICIPALITY", "en", ""),
            Entity("Saba", "BQ-SA", "SPECIAL MUNICIPALITY", "nl", ""),
            Entity("Saba", "BQ-SA", "SPECIAL MUNICIPALITY", "", ""),
        ),
        "BQ-SE": (
            Entity("Sint Eustatius", "BQ-SE", "SPECIAL MUNICIPALITY", "en", ""),
            Entity("Sint Eustatius", "BQ-SE", "SPECIAL MUNICIPALITY", "nl", ""),
            Entity("Sint Eustatius", "BQ-SE", "SPECIAL MUNICIPALITY", "", ""),
        ),
    }
