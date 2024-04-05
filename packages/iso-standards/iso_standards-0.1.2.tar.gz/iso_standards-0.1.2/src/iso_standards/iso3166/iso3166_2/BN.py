"""ISO 3166-2 BN standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BN
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BN-BE": (
            Entity("Belait", "BN-BE", "DISTRICT", "en", ""),
            Entity("Belait", "BN-BE", "DISTRICT", "ms", ""),
        ),
        "BN-BM": (
            Entity("Brunei dan Muara", "BN-BM", "DISTRICT", "ms", ""),
            Entity("Brunei-Muara", "BN-BM", "DISTRICT", "en", ""),
        ),
        "BN-TE": (
            Entity("Temburong", "BN-TE", "DISTRICT", "en", ""),
            Entity("Temburong", "BN-TE", "DISTRICT", "ms", ""),
        ),
        "BN-TU": (
            Entity("Tutong", "BN-TU", "DISTRICT", "en", ""),
            Entity("Tutong", "BN-TU", "DISTRICT", "ms", ""),
        ),
    }
