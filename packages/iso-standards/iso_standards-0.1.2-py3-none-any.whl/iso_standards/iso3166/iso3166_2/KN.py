"""ISO 3166-2 KN standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:KN
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "KN-01": (Entity("Christ Church Nichola Town", "KN-01", "PARISH", "en", "KN-K"),),
        "KN-02": (Entity("Saint Anne Sandy Point", "KN-02", "PARISH", "en", "KN-K"),),
        "KN-03": (Entity("Saint George Basseterre", "KN-03", "PARISH", "en", "KN-K"),),
        "KN-04": (Entity("Saint George Gingerland", "KN-04", "PARISH", "en", "KN-N"),),
        "KN-05": (Entity("Saint James Windward", "KN-05", "PARISH", "en", "KN-N"),),
        "KN-06": (Entity("Saint John Capisterre", "KN-06", "PARISH", "en", "KN-K"),),
        "KN-07": (Entity("Saint John Figtree", "KN-07", "PARISH", "en", "KN-N"),),
        "KN-08": (Entity("Saint Mary Cayon", "KN-08", "PARISH", "en", "KN-K"),),
        "KN-09": (Entity("Saint Paul Capisterre", "KN-09", "PARISH", "en", "KN-K"),),
        "KN-10": (Entity("Saint Paul Charlestown", "KN-10", "PARISH", "en", "KN-N"),),
        "KN-11": (Entity("Saint Peter Basseterre", "KN-11", "PARISH", "en", "KN-K"),),
        "KN-12": (Entity("Saint Thomas Lowland", "KN-12", "PARISH", "en", "KN-N"),),
        "KN-13": (Entity("Saint Thomas Middle Island", "KN-13", "PARISH", "en", "KN-K"),),
        "KN-15": (Entity("Trinity Palmetto Point", "KN-15", "PARISH", "en", "KN-K"),),
        "KN-K": (Entity("Saint Kitts", "KN-K", "STATE", "en", ""),),
        "KN-N": (Entity("Nevis", "KN-N", "STATE", "en", ""),),
    }
