"""ISO 3166-2 ZW standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:ZW
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "ZW-BU": (Entity("Bulawayo", "ZW-BU", "PROVINCE", "en", ""),),
        "ZW-HA": (Entity("Harare", "ZW-HA", "PROVINCE", "en", ""),),
        "ZW-MA": (Entity("Manicaland", "ZW-MA", "PROVINCE", "en", ""),),
        "ZW-MC": (Entity("Mashonaland Central", "ZW-MC", "PROVINCE", "en", ""),),
        "ZW-ME": (Entity("Mashonaland East", "ZW-ME", "PROVINCE", "en", ""),),
        "ZW-MI": (Entity("Midlands", "ZW-MI", "PROVINCE", "en", ""),),
        "ZW-MN": (Entity("Matabeleland North", "ZW-MN", "PROVINCE", "en", ""),),
        "ZW-MS": (Entity("Matabeleland South", "ZW-MS", "PROVINCE", "en", ""),),
        "ZW-MV": (Entity("Masvingo", "ZW-MV", "PROVINCE", "en", ""),),
        "ZW-MW": (Entity("Mashonaland West", "ZW-MW", "PROVINCE", "en", ""),),
    }
