"""ISO 3166-2 TJ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:TJ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "TJ-DU": (Entity("Dushanbe", "TJ-DU", "CAPITAL TERRITORY", "tg", ""),),
        "TJ-GB": (Entity("Kŭhistoni Badakhshon", "TJ-GB", "AUTONOMOUS REGION", "tg", ""),),
        "TJ-KT": (Entity("Khatlon", "TJ-KT", "REGION", "tg", ""),),
        "TJ-RA": (
            Entity(
                "nohiyahoi tobei jumhurí",
                "TJ-RA",
                "DISTRICTS UNDER REPUBLIC ADMINISTRATION",
                "tg",
                "",
            ),
        ),
        "TJ-SU": (Entity("Sughd", "TJ-SU", "REGION", "tg", ""),),
    }
