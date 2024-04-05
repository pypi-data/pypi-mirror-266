"""ISO 3166-2 SH standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SH
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SH-AC": (Entity("Ascension", "SH-AC", "GEOGRAPHICAL ENTITY", "en", ""),),
        "SH-HL": (Entity("Saint Helena", "SH-HL", "GEOGRAPHICAL ENTITY", "en", ""),),
        "SH-TA": (Entity("Tristan da Cunha", "SH-TA", "GEOGRAPHICAL ENTITY", "en", ""),),
    }
