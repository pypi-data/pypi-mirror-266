"""ISO 3166-2 FM standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:FM
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "FM-KSA": (Entity("Kosrae", "FM-KSA", "STATE", "en", ""),),
        "FM-PNI": (Entity("Pohnpei", "FM-PNI", "STATE", "en", ""),),
        "FM-TRK": (Entity("Chuuk", "FM-TRK", "STATE", "en", ""),),
        "FM-YAP": (Entity("Yap", "FM-YAP", "STATE", "en", ""),),
    }
