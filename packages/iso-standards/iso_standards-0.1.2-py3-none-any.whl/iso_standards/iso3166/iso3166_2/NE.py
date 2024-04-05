"""ISO 3166-2 NE standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:NE
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "NE-1": (Entity("Agadez", "NE-1", "REGION", "fr", ""),),
        "NE-2": (Entity("Diffa", "NE-2", "REGION", "fr", ""),),
        "NE-3": (Entity("Dosso", "NE-3", "REGION", "fr", ""),),
        "NE-4": (Entity("Maradi", "NE-4", "REGION", "fr", ""),),
        "NE-5": (Entity("Tahoua", "NE-5", "REGION", "fr", ""),),
        "NE-6": (Entity("Tillabéri", "NE-6", "REGION", "fr", ""),),
        "NE-7": (Entity("Zinder", "NE-7", "REGION", "fr", ""),),
        "NE-8": (Entity("Niamey", "NE-8", "URBAN COMMUNITY", "fr", ""),),
    }
