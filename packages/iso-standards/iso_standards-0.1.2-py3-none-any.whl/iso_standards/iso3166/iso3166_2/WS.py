"""ISO 3166-2 WS standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:WS
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "WS-AA": (
            Entity("A'ana", "WS-AA", "DISTRICT", "en", ""),
            Entity("A'ana", "WS-AA", "DISTRICT", "sm", ""),
        ),
        "WS-AL": (
            Entity("Aiga-i-le-Tai", "WS-AL", "DISTRICT", "en", ""),
            Entity("Aiga-i-le-Tai", "WS-AL", "DISTRICT", "sm", ""),
        ),
        "WS-AT": (
            Entity("Atua", "WS-AT", "DISTRICT", "en", ""),
            Entity("Atua", "WS-AT", "DISTRICT", "sm", ""),
        ),
        "WS-FA": (
            Entity("Fa'asaleleaga", "WS-FA", "DISTRICT", "en", ""),
            Entity("Fa'asaleleaga", "WS-FA", "DISTRICT", "sm", ""),
        ),
        "WS-GE": (
            Entity("Gaga'emauga", "WS-GE", "DISTRICT", "en", ""),
            Entity("Gaga'emauga", "WS-GE", "DISTRICT", "sm", ""),
        ),
        "WS-GI": (
            Entity("Gagaifomauga", "WS-GI", "DISTRICT", "en", ""),
            Entity("Gagaifomauga", "WS-GI", "DISTRICT", "sm", ""),
        ),
        "WS-PA": (
            Entity("Palauli", "WS-PA", "DISTRICT", "en", ""),
            Entity("Palauli", "WS-PA", "DISTRICT", "sm", ""),
        ),
        "WS-SA": (
            Entity("Satupa'itea", "WS-SA", "DISTRICT", "en", ""),
            Entity("Satupa'itea", "WS-SA", "DISTRICT", "sm", ""),
        ),
        "WS-TU": (
            Entity("Tuamasaga", "WS-TU", "DISTRICT", "en", ""),
            Entity("Tuamasaga", "WS-TU", "DISTRICT", "sm", ""),
        ),
        "WS-VF": (
            Entity("Va'a-o-Fonoti", "WS-VF", "DISTRICT", "en", ""),
            Entity("Va'a-o-Fonoti", "WS-VF", "DISTRICT", "sm", ""),
        ),
        "WS-VS": (
            Entity("Vaisigano", "WS-VS", "DISTRICT", "en", ""),
            Entity("Vaisigano", "WS-VS", "DISTRICT", "sm", ""),
        ),
    }
