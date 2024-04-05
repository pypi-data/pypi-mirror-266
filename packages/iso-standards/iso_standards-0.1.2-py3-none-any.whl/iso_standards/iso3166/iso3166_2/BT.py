"""ISO 3166-2 BT standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BT
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BT-11": (Entity("Paro", "BT-11", "DISTRICT", "dz", ""),),
        "BT-12": (Entity("Chhukha", "BT-12", "DISTRICT", "dz", ""),),
        "BT-13": (Entity("Haa", "BT-13", "DISTRICT", "dz", ""),),
        "BT-14": (Entity("Samtse", "BT-14", "DISTRICT", "dz", ""),),
        "BT-15": (Entity("Thimphu", "BT-15", "DISTRICT", "dz", ""),),
        "BT-21": (Entity("Tsirang", "BT-21", "DISTRICT", "dz", ""),),
        "BT-22": (Entity("Dagana", "BT-22", "DISTRICT", "dz", ""),),
        "BT-23": (Entity("Punakha", "BT-23", "DISTRICT", "dz", ""),),
        "BT-24": (Entity("Wangdue Phodrang", "BT-24", "DISTRICT", "dz", ""),),
        "BT-31": (Entity("Sarpang", "BT-31", "DISTRICT", "dz", ""),),
        "BT-32": (Entity("Trongsa", "BT-32", "DISTRICT", "dz", ""),),
        "BT-33": (Entity("Bumthang", "BT-33", "DISTRICT", "dz", ""),),
        "BT-34": (Entity("Zhemgang", "BT-34", "DISTRICT", "dz", ""),),
        "BT-41": (Entity("Trashigang", "BT-41", "DISTRICT", "dz", ""),),
        "BT-42": (Entity("Monggar", "BT-42", "DISTRICT", "dz", ""),),
        "BT-43": (Entity("Pema Gatshel", "BT-43", "DISTRICT", "dz", ""),),
        "BT-44": (Entity("Lhuentse", "BT-44", "DISTRICT", "dz", ""),),
        "BT-45": (Entity("Samdrup Jongkhar", "BT-45", "DISTRICT", "dz", ""),),
        "BT-GA": (Entity("Gasa", "BT-GA", "DISTRICT", "dz", ""),),
        "BT-TY": (Entity("Trashi Yangtse", "BT-TY", "DISTRICT", "dz", ""),),
    }
