"""ISO 3166-2 LC standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:LC
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "LC-01": (Entity("Anse la Raye", "LC-01", "DISTRICT", "en", ""),),
        "LC-02": (Entity("Castries", "LC-02", "DISTRICT", "en", ""),),
        "LC-03": (Entity("Choiseul", "LC-03", "DISTRICT", "en", ""),),
        "LC-05": (Entity("Dennery", "LC-05", "DISTRICT", "en", ""),),
        "LC-06": (Entity("Gros Islet", "LC-06", "DISTRICT", "en", ""),),
        "LC-07": (Entity("Laborie", "LC-07", "DISTRICT", "en", ""),),
        "LC-08": (Entity("Micoud", "LC-08", "DISTRICT", "en", ""),),
        "LC-10": (Entity("Soufrière", "LC-10", "DISTRICT", "en", ""),),
        "LC-11": (Entity("Vieux Fort", "LC-11", "DISTRICT", "en", ""),),
        "LC-12": (Entity("Canaries", "LC-12", "DISTRICT", "en", ""),),
    }
