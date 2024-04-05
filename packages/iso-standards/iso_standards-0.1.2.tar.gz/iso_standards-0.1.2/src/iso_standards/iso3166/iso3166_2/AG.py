"""ISO 3166-2 AG standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:AG
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "AG-03": (Entity("Saint George", "AG-03", "PARISH", "en", ""),),
        "AG-04": (Entity("Saint John", "AG-04", "PARISH", "en", ""),),
        "AG-05": (Entity("Saint Mary", "AG-05", "PARISH", "en", ""),),
        "AG-06": (Entity("Saint Paul", "AG-06", "PARISH", "en", ""),),
        "AG-07": (Entity("Saint Peter", "AG-07", "PARISH", "en", ""),),
        "AG-08": (Entity("Saint Philip", "AG-08", "PARISH", "en", ""),),
        "AG-10": (Entity("Barbuda", "AG-10", "DEPENDENCY", "en", ""),),
        "AG-11": (Entity("Redonda", "AG-11", "DEPENDENCY", "en", ""),),
    }
