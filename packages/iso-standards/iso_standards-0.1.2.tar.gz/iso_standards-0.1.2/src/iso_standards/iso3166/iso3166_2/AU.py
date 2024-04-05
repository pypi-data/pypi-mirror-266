"""ISO 3166-2 AU standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:AU
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "AU-ACT": (Entity("Australian Capital Territory", "AU-ACT", "TERRITORY", "en", ""),),
        "AU-NSW": (Entity("New South Wales", "AU-NSW", "STATE", "en", ""),),
        "AU-NT": (Entity("Northern Territory", "AU-NT", "TERRITORY", "en", ""),),
        "AU-QLD": (Entity("Queensland", "AU-QLD", "STATE", "en", ""),),
        "AU-SA": (Entity("South Australia", "AU-SA", "STATE", "en", ""),),
        "AU-TAS": (Entity("Tasmania", "AU-TAS", "STATE", "en", ""),),
        "AU-VIC": (Entity("Victoria", "AU-VIC", "STATE", "en", ""),),
        "AU-WA": (Entity("Western Australia", "AU-WA", "STATE", "en", ""),),
    }
