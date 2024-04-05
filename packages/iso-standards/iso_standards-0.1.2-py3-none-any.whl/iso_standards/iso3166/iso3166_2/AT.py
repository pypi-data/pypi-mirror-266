"""ISO 3166-2 AT standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:AT
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "AT-1": (Entity("Burgenland", "AT-1", "STATE", "de", ""),),
        "AT-2": (Entity("Kärnten", "AT-2", "STATE", "de", ""),),
        "AT-3": (Entity("Niederösterreich", "AT-3", "STATE", "de", ""),),
        "AT-4": (Entity("Oberösterreich", "AT-4", "STATE", "de", ""),),
        "AT-5": (Entity("Salzburg", "AT-5", "STATE", "de", ""),),
        "AT-6": (Entity("Steiermark", "AT-6", "STATE", "de", ""),),
        "AT-7": (Entity("Tirol", "AT-7", "STATE", "de", ""),),
        "AT-8": (Entity("Vorarlberg", "AT-8", "STATE", "de", ""),),
        "AT-9": (Entity("Wien", "AT-9", "STATE", "de", ""),),
    }
