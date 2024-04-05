"""ISO 3166-2 UM standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:UM
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "UM-67": (Entity("Johnston Atoll", "UM-67", "ISLANDS, GROUPS OF ISLANDS", "en", ""),),
        "UM-71": (Entity("Midway Islands", "UM-71", "ISLANDS, GROUPS OF ISLANDS", "en", ""),),
        "UM-76": (Entity("Navassa Island", "UM-76", "ISLANDS, GROUPS OF ISLANDS", "en", ""),),
        "UM-79": (Entity("Wake Island", "UM-79", "ISLANDS, GROUPS OF ISLANDS", "en", ""),),
        "UM-81": (Entity("Baker Island", "UM-81", "ISLANDS, GROUPS OF ISLANDS", "en", ""),),
        "UM-84": (Entity("Howland Island", "UM-84", "ISLANDS, GROUPS OF ISLANDS", "en", ""),),
        "UM-86": (Entity("Jarvis Island", "UM-86", "ISLANDS, GROUPS OF ISLANDS", "en", ""),),
        "UM-89": (Entity("Kingman Reef", "UM-89", "ISLANDS, GROUPS OF ISLANDS", "en", ""),),
        "UM-95": (Entity("Palmyra Atoll", "UM-95", "ISLANDS, GROUPS OF ISLANDS", "en", ""),),
    }
