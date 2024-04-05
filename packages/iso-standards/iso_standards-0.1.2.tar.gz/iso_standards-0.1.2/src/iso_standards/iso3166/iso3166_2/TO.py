"""ISO 3166-2 TO standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:TO
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "TO-01": (
            Entity("'Eua", "TO-01", "DIVISION", "en", ""),
            Entity("'Eua", "TO-01", "DIVISION", "to", ""),
        ),
        "TO-02": (
            Entity("Ha'apai", "TO-02", "DIVISION", "en", ""),
            Entity("Ha'apai", "TO-02", "DIVISION", "to", ""),
        ),
        "TO-03": (
            Entity("Niuas", "TO-03", "DIVISION", "en", ""),
            Entity("Niuas", "TO-03", "DIVISION", "to", ""),
        ),
        "TO-04": (
            Entity("Tongatapu", "TO-04", "DIVISION", "en", ""),
            Entity("Tongatapu", "TO-04", "DIVISION", "to", ""),
        ),
        "TO-05": (
            Entity("Vava'u", "TO-05", "DIVISION", "en", ""),
            Entity("Vava'u", "TO-05", "DIVISION", "to", ""),
        ),
    }
