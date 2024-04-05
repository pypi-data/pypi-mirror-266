"""ISO 3166-2 NP standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:NP
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "NP-P1": (
            Entity("Koshi", "NP-P1", "PROVINCE", "en", ""),
            Entity("Koshī", "NP-P1", "PROVINCE", "ne", ""),
        ),
        "NP-P2": (
            Entity("Madhesh", "NP-P2", "PROVINCE", "en", ""),
            Entity("Madhesh", "NP-P2", "PROVINCE", "ne", ""),
        ),
        "NP-P3": (
            Entity("Bagmati", "NP-P3", "PROVINCE", "en", ""),
            Entity("Bāgmatī", "NP-P3", "PROVINCE", "ne", ""),
        ),
        "NP-P4": (
            Entity("Gandaki", "NP-P4", "PROVINCE", "en", ""),
            Entity("Gaṇḍakī", "NP-P4", "PROVINCE", "ne", ""),
        ),
        "NP-P5": (
            Entity("Lumbini", "NP-P5", "PROVINCE", "en", ""),
            Entity("Lumbinī", "NP-P5", "PROVINCE", "ne", ""),
        ),
        "NP-P6": (
            Entity("Karnali", "NP-P6", "PROVINCE", "en", ""),
            Entity("Karṇālī", "NP-P6", "PROVINCE", "ne", ""),
        ),
        "NP-P7": (
            Entity("Sudurpashchim", "NP-P7", "PROVINCE", "en", ""),
            Entity("Sudūrpashchim", "NP-P7", "PROVINCE", "ne", ""),
        ),
    }
