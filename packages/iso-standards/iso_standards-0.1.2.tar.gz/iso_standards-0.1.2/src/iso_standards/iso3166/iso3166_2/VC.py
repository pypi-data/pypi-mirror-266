"""ISO 3166-2 VC standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:VC
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "VC-01": (Entity("Charlotte", "VC-01", "PARISH", "en", ""),),
        "VC-02": (Entity("Saint Andrew", "VC-02", "PARISH", "en", ""),),
        "VC-03": (Entity("Saint David", "VC-03", "PARISH", "en", ""),),
        "VC-04": (Entity("Saint George", "VC-04", "PARISH", "en", ""),),
        "VC-05": (Entity("Saint Patrick", "VC-05", "PARISH", "en", ""),),
        "VC-06": (Entity("Grenadines", "VC-06", "PARISH", "en", ""),),
    }
