"""ISO 3166-2 NR standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:NR
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "NR-01": (
            Entity("Aiwo", "NR-01", "DISTRICT", "en", ""),
            Entity("Aiwo", "NR-01", "DISTRICT", "na", ""),
        ),
        "NR-02": (
            Entity("Anabar", "NR-02", "DISTRICT", "en", ""),
            Entity("Anabar", "NR-02", "DISTRICT", "na", ""),
        ),
        "NR-03": (
            Entity("Anetan", "NR-03", "DISTRICT", "en", ""),
            Entity("Anetan", "NR-03", "DISTRICT", "na", ""),
        ),
        "NR-04": (
            Entity("Anibare", "NR-04", "DISTRICT", "en", ""),
            Entity("Anibare", "NR-04", "DISTRICT", "na", ""),
        ),
        "NR-05": (
            Entity("Baitsi", "NR-05", "DISTRICT", "en", ""),
            Entity("Baitsi", "NR-05", "DISTRICT", "na", ""),
        ),
        "NR-06": (
            Entity("Boe", "NR-06", "DISTRICT", "en", ""),
            Entity("Boe", "NR-06", "DISTRICT", "na", ""),
        ),
        "NR-07": (
            Entity("Buada", "NR-07", "DISTRICT", "en", ""),
            Entity("Buada", "NR-07", "DISTRICT", "na", ""),
        ),
        "NR-08": (
            Entity("Denigomodu", "NR-08", "DISTRICT", "en", ""),
            Entity("Denigomodu", "NR-08", "DISTRICT", "na", ""),
        ),
        "NR-09": (
            Entity("Ewa", "NR-09", "DISTRICT", "en", ""),
            Entity("Ewa", "NR-09", "DISTRICT", "na", ""),
        ),
        "NR-10": (
            Entity("Ijuw", "NR-10", "DISTRICT", "en", ""),
            Entity("Ijuw", "NR-10", "DISTRICT", "na", ""),
        ),
        "NR-11": (
            Entity("Meneng", "NR-11", "DISTRICT", "en", ""),
            Entity("Meneng", "NR-11", "DISTRICT", "na", ""),
        ),
        "NR-12": (
            Entity("Nibok", "NR-12", "DISTRICT", "en", ""),
            Entity("Nibok", "NR-12", "DISTRICT", "na", ""),
        ),
        "NR-13": (
            Entity("Uaboe", "NR-13", "DISTRICT", "en", ""),
            Entity("Uaboe", "NR-13", "DISTRICT", "na", ""),
        ),
        "NR-14": (
            Entity("Yaren", "NR-14", "DISTRICT", "en", ""),
            Entity("Yaren", "NR-14", "DISTRICT", "na", ""),
        ),
    }
