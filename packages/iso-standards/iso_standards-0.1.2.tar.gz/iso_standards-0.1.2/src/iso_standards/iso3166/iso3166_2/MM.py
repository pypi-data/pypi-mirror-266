"""ISO 3166-2 MM standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:MM
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "MM-01": (Entity("Sagaing", "MM-01", "REGION", "my", ""),),
        "MM-02": (Entity("Bago", "MM-02", "REGION", "my", ""),),
        "MM-03": (Entity("Magway", "MM-03", "REGION", "my", ""),),
        "MM-04": (Entity("Mandalay", "MM-04", "REGION", "my", ""),),
        "MM-05": (Entity("Tanintharyi", "MM-05", "REGION", "my", ""),),
        "MM-06": (Entity("Yangon", "MM-06", "REGION", "my", ""),),
        "MM-07": (Entity("Ayeyarwady", "MM-07", "REGION", "my", ""),),
        "MM-11": (Entity("Kachin", "MM-11", "STATE", "my", ""),),
        "MM-12": (Entity("Kayah", "MM-12", "STATE", "my", ""),),
        "MM-13": (Entity("Kayin", "MM-13", "STATE", "my", ""),),
        "MM-14": (Entity("Chin", "MM-14", "STATE", "my", ""),),
        "MM-15": (Entity("Mon", "MM-15", "STATE", "my", ""),),
        "MM-16": (Entity("Rakhine", "MM-16", "STATE", "my", ""),),
        "MM-17": (Entity("Shan", "MM-17", "STATE", "my", ""),),
        "MM-18": (Entity("Nay Pyi Taw", "MM-18", "UNION TERRITORY", "my", ""),),
    }
