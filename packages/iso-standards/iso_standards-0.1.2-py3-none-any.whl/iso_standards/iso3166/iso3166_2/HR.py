"""ISO 3166-2 HR standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:HR
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "HR-01": (Entity("Zagrebačka županija", "HR-01", "COUNTY", "hr", ""),),
        "HR-02": (Entity("Krapinsko-zagorska županija", "HR-02", "COUNTY", "hr", ""),),
        "HR-03": (Entity("Sisačko-moslavačka županija", "HR-03", "COUNTY", "hr", ""),),
        "HR-04": (Entity("Karlovačka županija", "HR-04", "COUNTY", "hr", ""),),
        "HR-05": (Entity("Varaždinska županija", "HR-05", "COUNTY", "hr", ""),),
        "HR-06": (Entity("Koprivničko-križevačka županija", "HR-06", "COUNTY", "hr", ""),),
        "HR-07": (Entity("Bjelovarsko-bilogorska županija", "HR-07", "COUNTY", "hr", ""),),
        "HR-08": (Entity("Primorsko-goranska županija", "HR-08", "COUNTY", "hr", ""),),
        "HR-09": (Entity("Ličko-senjska županija", "HR-09", "COUNTY", "hr", ""),),
        "HR-10": (Entity("Virovitičko-podravska županija", "HR-10", "COUNTY", "hr", ""),),
        "HR-11": (Entity("Požeško-slavonska županija", "HR-11", "COUNTY", "hr", ""),),
        "HR-12": (Entity("Brodsko-posavska županija", "HR-12", "COUNTY", "hr", ""),),
        "HR-13": (Entity("Zadarska županija", "HR-13", "COUNTY", "hr", ""),),
        "HR-14": (Entity("Osječko-baranjska županija", "HR-14", "COUNTY", "hr", ""),),
        "HR-15": (Entity("Šibensko-kninska županija", "HR-15", "COUNTY", "hr", ""),),
        "HR-16": (Entity("Vukovarsko-srijemska županija", "HR-16", "COUNTY", "hr", ""),),
        "HR-17": (Entity("Splitsko-dalmatinska županija", "HR-17", "COUNTY", "hr", ""),),
        "HR-18": (Entity("Istarska županija", "HR-18", "COUNTY", "hr", ""),),
        "HR-19": (Entity("Dubrovačko-neretvanska županija", "HR-19", "COUNTY", "hr", ""),),
        "HR-20": (Entity("Međimurska županija", "HR-20", "COUNTY", "hr", ""),),
        "HR-21": (Entity("Grad Zagreb", "HR-21", "CITY", "hr", ""),),
    }
