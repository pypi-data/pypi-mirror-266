"""ISO 3166-2 LI standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:LI
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "LI-01": (Entity("Balzers", "LI-01", "COMMUNE", "de", ""),),
        "LI-02": (Entity("Eschen", "LI-02", "COMMUNE", "de", ""),),
        "LI-03": (Entity("Gamprin", "LI-03", "COMMUNE", "de", ""),),
        "LI-04": (Entity("Mauren", "LI-04", "COMMUNE", "de", ""),),
        "LI-05": (Entity("Planken", "LI-05", "COMMUNE", "de", ""),),
        "LI-06": (Entity("Ruggell", "LI-06", "COMMUNE", "de", ""),),
        "LI-07": (Entity("Schaan", "LI-07", "COMMUNE", "de", ""),),
        "LI-08": (Entity("Schellenberg", "LI-08", "COMMUNE", "de", ""),),
        "LI-09": (Entity("Triesen", "LI-09", "COMMUNE", "de", ""),),
        "LI-10": (Entity("Triesenberg", "LI-10", "COMMUNE", "de", ""),),
        "LI-11": (Entity("Vaduz", "LI-11", "COMMUNE", "de", ""),),
    }
