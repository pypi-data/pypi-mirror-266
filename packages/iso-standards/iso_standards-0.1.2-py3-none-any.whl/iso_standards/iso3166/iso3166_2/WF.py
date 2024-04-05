"""ISO 3166-2 WF standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:WF
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "WF-AL": (Entity("Alo", "WF-AL", "ADMINISTRATIVE PRECINCT", "fr", ""),),
        "WF-SG": (Entity("Sigave", "WF-SG", "ADMINISTRATIVE PRECINCT", "fr", ""),),
        "WF-UV": (Entity("Uvea", "WF-UV", "ADMINISTRATIVE PRECINCT", "fr", ""),),
    }
