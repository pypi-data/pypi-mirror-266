"""ISO 3166-2 BG standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BG
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BG-01": (Entity("Blagoevgrad", "BG-01", "DISTRICT", "bg", ""),),
        "BG-02": (Entity("Burgas", "BG-02", "DISTRICT", "bg", ""),),
        "BG-03": (Entity("Varna", "BG-03", "DISTRICT", "bg", ""),),
        "BG-04": (Entity("Veliko Tarnovo", "BG-04", "DISTRICT", "bg", ""),),
        "BG-05": (Entity("Vidin", "BG-05", "DISTRICT", "bg", ""),),
        "BG-06": (Entity("Vratsa", "BG-06", "DISTRICT", "bg", ""),),
        "BG-07": (Entity("Gabrovo", "BG-07", "DISTRICT", "bg", ""),),
        "BG-08": (Entity("Dobrich", "BG-08", "DISTRICT", "bg", ""),),
        "BG-09": (Entity("Kardzhali", "BG-09", "DISTRICT", "bg", ""),),
        "BG-10": (Entity("Kyustendil", "BG-10", "DISTRICT", "bg", ""),),
        "BG-11": (Entity("Lovech", "BG-11", "DISTRICT", "bg", ""),),
        "BG-12": (Entity("Montana", "BG-12", "DISTRICT", "bg", ""),),
        "BG-13": (Entity("Pazardzhik", "BG-13", "DISTRICT", "bg", ""),),
        "BG-14": (Entity("Pernik", "BG-14", "DISTRICT", "bg", ""),),
        "BG-15": (Entity("Pleven", "BG-15", "DISTRICT", "bg", ""),),
        "BG-16": (Entity("Plovdiv", "BG-16", "DISTRICT", "bg", ""),),
        "BG-17": (Entity("Razgrad", "BG-17", "DISTRICT", "bg", ""),),
        "BG-18": (Entity("Ruse", "BG-18", "DISTRICT", "bg", ""),),
        "BG-19": (Entity("Silistra", "BG-19", "DISTRICT", "bg", ""),),
        "BG-20": (Entity("Sliven", "BG-20", "DISTRICT", "bg", ""),),
        "BG-21": (Entity("Smolyan", "BG-21", "DISTRICT", "bg", ""),),
        "BG-22": (Entity("Sofia", "BG-22", "DISTRICT", "bg", ""),),
        "BG-23": (Entity("Sofia", "BG-23", "DISTRICT", "bg", ""),),
        "BG-24": (Entity("Stara Zagora", "BG-24", "DISTRICT", "bg", ""),),
        "BG-25": (Entity("Targovishte", "BG-25", "DISTRICT", "bg", ""),),
        "BG-26": (Entity("Haskovo", "BG-26", "DISTRICT", "bg", ""),),
        "BG-27": (Entity("Shumen", "BG-27", "DISTRICT", "bg", ""),),
        "BG-28": (Entity("Yambol", "BG-28", "DISTRICT", "bg", ""),),
    }
