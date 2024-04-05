"""ISO 3166-2 BZ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BZ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BZ-BZ": (Entity("Belize", "BZ-BZ", "DISTRICT", "en", ""),),
        "BZ-CY": (Entity("Cayo", "BZ-CY", "DISTRICT", "en", ""),),
        "BZ-CZL": (Entity("Corozal", "BZ-CZL", "DISTRICT", "en", ""),),
        "BZ-OW": (Entity("Orange Walk", "BZ-OW", "DISTRICT", "en", ""),),
        "BZ-SC": (Entity("Stann Creek", "BZ-SC", "DISTRICT", "en", ""),),
        "BZ-TOL": (Entity("Toledo", "BZ-TOL", "DISTRICT", "en", ""),),
    }
