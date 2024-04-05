"""ISO 3166-2 MY standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:MY
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "MY-01": (Entity("Johor", "MY-01", "STATE", "ms", ""),),
        "MY-02": (Entity("Kedah", "MY-02", "STATE", "ms", ""),),
        "MY-03": (Entity("Kelantan", "MY-03", "STATE", "ms", ""),),
        "MY-04": (Entity("Melaka", "MY-04", "STATE", "ms", ""),),
        "MY-05": (Entity("Negeri Sembilan", "MY-05", "STATE", "ms", ""),),
        "MY-06": (Entity("Pahang", "MY-06", "STATE", "ms", ""),),
        "MY-07": (Entity("Pulau Pinang", "MY-07", "STATE", "ms", ""),),
        "MY-08": (Entity("Perak", "MY-08", "STATE", "ms", ""),),
        "MY-09": (Entity("Perlis", "MY-09", "STATE", "ms", ""),),
        "MY-10": (Entity("Selangor", "MY-10", "STATE", "ms", ""),),
        "MY-11": (Entity("Terengganu", "MY-11", "STATE", "ms", ""),),
        "MY-12": (Entity("Sabah", "MY-12", "STATE", "ms", ""),),
        "MY-13": (Entity("Sarawak", "MY-13", "STATE", "ms", ""),),
        "MY-14": (
            Entity("Wilayah Persekutuan Kuala Lumpur", "MY-14", "FEDERAL TERRITORY", "ms", ""),
        ),
        "MY-15": (Entity("Wilayah Persekutuan Labuan", "MY-15", "FEDERAL TERRITORY", "ms", ""),),
        "MY-16": (Entity("Wilayah Persekutuan Putrajaya", "MY-16", "FEDERAL TERRITORY", "ms", ""),),
    }
