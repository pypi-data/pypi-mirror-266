"""ISO 3166-2 LU standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:LU
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "LU-CA": (
            Entity("Capellen", "LU-CA", "CANTON", "de", ""),
            Entity("Capellen", "LU-CA", "CANTON", "fr", ""),
            Entity("Kapellen", "LU-CA", "CANTON", "lb", ""),
        ),
        "LU-CL": (
            Entity("Clerf", "LU-CL", "CANTON", "de", ""),
            Entity("Clervaux", "LU-CL", "CANTON", "fr", ""),
            Entity("Klierf", "LU-CL", "CANTON", "lb", ""),
        ),
        "LU-DI": (
            Entity("Diekirch", "LU-DI", "CANTON", "de", ""),
            Entity("Diekirch", "LU-DI", "CANTON", "fr", ""),
            Entity("Diekrech", "LU-DI", "CANTON", "lb", ""),
        ),
        "LU-EC": (
            Entity("Echternach", "LU-EC", "CANTON", "de", ""),
            Entity("Echternach", "LU-EC", "CANTON", "fr", ""),
            Entity("Iechternach", "LU-EC", "CANTON", "lb", ""),
        ),
        "LU-ES": (
            Entity("Esch an der Alzette", "LU-ES", "CANTON", "de", ""),
            Entity("Esch-Uelzecht", "LU-ES", "CANTON", "lb", ""),
            Entity("Esch-sur-Alzette", "LU-ES", "CANTON", "fr", ""),
        ),
        "LU-GR": (
            Entity("Grevenmacher", "LU-GR", "CANTON", "de", ""),
            Entity("Grevenmacher", "LU-GR", "CANTON", "fr", ""),
            Entity("Gréivemaacher", "LU-GR", "CANTON", "lb", ""),
        ),
        "LU-LU": (
            Entity("Luxembourg", "LU-LU", "CANTON", "fr", ""),
            Entity("Luxemburg", "LU-LU", "CANTON", "de", ""),
            Entity("Lëtzebuerg", "LU-LU", "CANTON", "lb", ""),
        ),
        "LU-ME": (
            Entity("Mersch", "LU-ME", "CANTON", "de", ""),
            Entity("Mersch", "LU-ME", "CANTON", "fr", ""),
            Entity("Miersch", "LU-ME", "CANTON", "lb", ""),
        ),
        "LU-RD": (
            Entity("Redange", "LU-RD", "CANTON", "fr", ""),
            Entity("Redingen", "LU-RD", "CANTON", "de", ""),
            Entity("Réiden-Atert", "LU-RD", "CANTON", "lb", ""),
        ),
        "LU-RM": (
            Entity("Remich", "LU-RM", "CANTON", "de", ""),
            Entity("Remich", "LU-RM", "CANTON", "fr", ""),
            Entity("Réimech", "LU-RM", "CANTON", "lb", ""),
        ),
        "LU-VD": (
            Entity("Veianen", "LU-VD", "CANTON", "lb", ""),
            Entity("Vianden", "LU-VD", "CANTON", "de", ""),
            Entity("Vianden", "LU-VD", "CANTON", "fr", ""),
        ),
        "LU-WI": (
            Entity("Wiltz", "LU-WI", "CANTON", "de", ""),
            Entity("Wiltz", "LU-WI", "CANTON", "fr", ""),
            Entity("Wolz", "LU-WI", "CANTON", "lb", ""),
        ),
    }
