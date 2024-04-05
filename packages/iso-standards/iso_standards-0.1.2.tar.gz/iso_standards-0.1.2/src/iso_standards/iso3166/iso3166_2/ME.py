"""ISO 3166-2 ME standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:ME
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "ME-01": (Entity("Andrijevica", "ME-01", "MUNICIPALITY", "", ""),),
        "ME-02": (Entity("Bar", "ME-02", "MUNICIPALITY", "", ""),),
        "ME-03": (Entity("Berane", "ME-03", "MUNICIPALITY", "", ""),),
        "ME-04": (Entity("Bijelo Polje", "ME-04", "MUNICIPALITY", "", ""),),
        "ME-05": (Entity("Budva", "ME-05", "MUNICIPALITY", "", ""),),
        "ME-06": (Entity("Cetinje", "ME-06", "MUNICIPALITY", "", ""),),
        "ME-07": (Entity("Danilovgrad", "ME-07", "MUNICIPALITY", "", ""),),
        "ME-08": (Entity("Herceg-Novi", "ME-08", "MUNICIPALITY", "", ""),),
        "ME-09": (Entity("Kolašin", "ME-09", "MUNICIPALITY", "", ""),),
        "ME-10": (Entity("Kotor", "ME-10", "MUNICIPALITY", "", ""),),
        "ME-11": (Entity("Mojkovac", "ME-11", "MUNICIPALITY", "", ""),),
        "ME-12": (Entity("Nikšić", "ME-12", "MUNICIPALITY", "", ""),),
        "ME-13": (Entity("Plav", "ME-13", "MUNICIPALITY", "", ""),),
        "ME-14": (Entity("Pljevlja", "ME-14", "MUNICIPALITY", "", ""),),
        "ME-15": (Entity("Plužine", "ME-15", "MUNICIPALITY", "", ""),),
        "ME-16": (Entity("Podgorica", "ME-16", "MUNICIPALITY", "", ""),),
        "ME-17": (Entity("Rožaje", "ME-17", "MUNICIPALITY", "", ""),),
        "ME-18": (Entity("Šavnik", "ME-18", "MUNICIPALITY", "", ""),),
        "ME-19": (Entity("Tivat", "ME-19", "MUNICIPALITY", "", ""),),
        "ME-20": (Entity("Ulcinj", "ME-20", "MUNICIPALITY", "", ""),),
        "ME-21": (Entity("Žabljak", "ME-21", "MUNICIPALITY", "", ""),),
        "ME-22": (Entity("Gusinje", "ME-22", "MUNICIPALITY", "", ""),),
        "ME-23": (Entity("Petnjica", "ME-23", "MUNICIPALITY", "", ""),),
        "ME-24": (Entity("Tuzi", "ME-24", "MUNICIPALITY", "", ""),),
        "ME-25": (Entity("Zeta", "ME-25", "MUNICIPALITY", "", ""),),
    }
