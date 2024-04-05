"""ISO 3166-2 CY standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CY
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CY-01": (
            Entity("Lefkosia", "CY-01", "DISTRICT", "el", ""),
            Entity("Lefkoşa", "CY-01", "DISTRICT", "tr", ""),
        ),
        "CY-02": (
            Entity("Lemesos", "CY-02", "DISTRICT", "el", ""),
            Entity("Leymasun", "CY-02", "DISTRICT", "tr", ""),
        ),
        "CY-03": (
            Entity("Larnaka", "CY-03", "DISTRICT", "el", ""),
            Entity("Larnaka", "CY-03", "DISTRICT", "tr", ""),
        ),
        "CY-04": (
            Entity("Ammochostos", "CY-04", "DISTRICT", "el", ""),
            Entity("Mağusa", "CY-04", "DISTRICT", "tr", ""),
        ),
        "CY-05": (
            Entity("Baf", "CY-05", "DISTRICT", "tr", ""),
            Entity("Pafos", "CY-05", "DISTRICT", "el", ""),
        ),
        "CY-06": (
            Entity("Girne", "CY-06", "DISTRICT", "tr", ""),
            Entity("Keryneia", "CY-06", "DISTRICT", "el", ""),
        ),
    }
