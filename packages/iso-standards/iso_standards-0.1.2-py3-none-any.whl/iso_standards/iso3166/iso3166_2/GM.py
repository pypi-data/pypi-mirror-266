"""ISO 3166-2 GM standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:GM
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "GM-B": (Entity("Banjul", "GM-B", "CITY", "en", ""),),
        "GM-L": (Entity("Lower River", "GM-L", "DIVISION", "en", ""),),
        "GM-M": (Entity("Central River", "GM-M", "DIVISION", "en", ""),),
        "GM-N": (Entity("North Bank", "GM-N", "DIVISION", "en", ""),),
        "GM-U": (Entity("Upper River", "GM-U", "DIVISION", "en", ""),),
        "GM-W": (Entity("Western", "GM-W", "DIVISION", "en", ""),),
    }
