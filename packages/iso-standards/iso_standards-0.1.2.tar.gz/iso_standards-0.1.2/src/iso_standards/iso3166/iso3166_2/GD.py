"""ISO 3166-2 GD standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:GD
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "GD-01": (Entity("Saint Andrew", "GD-01", "PARISH", "en", ""),),
        "GD-02": (Entity("Saint David", "GD-02", "PARISH", "en", ""),),
        "GD-03": (Entity("Saint George", "GD-03", "PARISH", "en", ""),),
        "GD-04": (Entity("Saint John", "GD-04", "PARISH", "en", ""),),
        "GD-05": (Entity("Saint Mark", "GD-05", "PARISH", "en", ""),),
        "GD-06": (Entity("Saint Patrick", "GD-06", "PARISH", "en", ""),),
        "GD-10": (Entity("Southern Grenadine Islands", "GD-10", "DEPENDENCY", "en", ""),),
    }
