"""ISO 3166-2 AM standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:AM
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "AM-AG": (Entity("Aragac̣otn", "AM-AG", "REGION", "hy", ""),),
        "AM-AR": (Entity("Ararat", "AM-AR", "REGION", "hy", ""),),
        "AM-AV": (Entity("Armavir", "AM-AV", "REGION", "hy", ""),),
        "AM-ER": (Entity("Erevan", "AM-ER", "CITY", "hy", ""),),
        "AM-GR": (Entity("Geġark'unik'", "AM-GR", "REGION", "hy", ""),),
        "AM-KT": (Entity("Kotayk'", "AM-KT", "REGION", "hy", ""),),
        "AM-LO": (Entity("Loṙi", "AM-LO", "REGION", "hy", ""),),
        "AM-SH": (Entity("Širak", "AM-SH", "REGION", "hy", ""),),
        "AM-SU": (Entity("Syunik'", "AM-SU", "REGION", "hy", ""),),
        "AM-TV": (Entity("Tavuš", "AM-TV", "REGION", "hy", ""),),
        "AM-VD": (Entity("Vayoć Jor", "AM-VD", "REGION", "hy", ""),),
    }
