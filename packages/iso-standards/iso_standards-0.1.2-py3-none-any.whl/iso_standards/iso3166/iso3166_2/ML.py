"""ISO 3166-2 ML standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:ML
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "ML-1": (Entity("Kayes", "ML-1", "REGION", "fr", ""),),
        "ML-10": (Entity("Taoudénit", "ML-10", "REGION", "fr", ""),),
        "ML-2": (Entity("Koulikoro", "ML-2", "REGION", "fr", ""),),
        "ML-3": (Entity("Sikasso", "ML-3", "REGION", "fr", ""),),
        "ML-4": (Entity("Ségou", "ML-4", "REGION", "fr", ""),),
        "ML-5": (Entity("Mopti", "ML-5", "REGION", "fr", ""),),
        "ML-6": (Entity("Tombouctou", "ML-6", "REGION", "fr", ""),),
        "ML-7": (Entity("Gao", "ML-7", "REGION", "fr", ""),),
        "ML-8": (Entity("Kidal", "ML-8", "REGION", "fr", ""),),
        "ML-9": (Entity("Ménaka", "ML-9", "REGION", "fr", ""),),
        "ML-BKO": (Entity("Bamako", "ML-BKO", "DISTRICT", "fr", ""),),
    }
