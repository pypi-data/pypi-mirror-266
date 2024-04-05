"""ISO 3166-2 GR standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:GR
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "GR-69": (Entity("Ágion Óros", "GR-69", "SELF-GOVERNED PART", "el", ""),),
        "GR-A": (
            Entity("Anatolikí Makedonía kai Thráki", "GR-A", "ADMINISTRATIVE REGION", "el", ""),
        ),
        "GR-B": (Entity("Kentrikí Makedonía", "GR-B", "ADMINISTRATIVE REGION", "el", ""),),
        "GR-C": (Entity("Dytikí Makedonía", "GR-C", "ADMINISTRATIVE REGION", "el", ""),),
        "GR-D": (Entity("Ípeiros", "GR-D", "ADMINISTRATIVE REGION", "el", ""),),
        "GR-E": (Entity("Thessalía", "GR-E", "ADMINISTRATIVE REGION", "el", ""),),
        "GR-F": (Entity("Ionía Nísia", "GR-F", "ADMINISTRATIVE REGION", "el", ""),),
        "GR-G": (Entity("Dytikí Elláda", "GR-G", "ADMINISTRATIVE REGION", "el", ""),),
        "GR-H": (Entity("Stereá Elláda", "GR-H", "ADMINISTRATIVE REGION", "el", ""),),
        "GR-I": (Entity("Attikí", "GR-I", "ADMINISTRATIVE REGION", "el", ""),),
        "GR-J": (Entity("Pelopónnisos", "GR-J", "ADMINISTRATIVE REGION", "el", ""),),
        "GR-K": (Entity("Vóreio Aigaío", "GR-K", "ADMINISTRATIVE REGION", "el", ""),),
        "GR-L": (Entity("Nótio Aigaío", "GR-L", "ADMINISTRATIVE REGION", "el", ""),),
        "GR-M": (Entity("Kríti", "GR-M", "ADMINISTRATIVE REGION", "el", ""),),
    }
