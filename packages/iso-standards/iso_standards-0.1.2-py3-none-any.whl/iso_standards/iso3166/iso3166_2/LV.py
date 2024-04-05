"""ISO 3166-2 LV standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:LV
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "LV-002": (Entity("Aizkraukles novads", "LV-002", "MUNICIPALITY", "lv", ""),),
        "LV-007": (Entity("Alūksnes novads", "LV-007", "MUNICIPALITY", "lv", ""),),
        "LV-011": (Entity("Ādažu novads", "LV-011", "MUNICIPALITY", "lv", ""),),
        "LV-015": (Entity("Balvu novads", "LV-015", "MUNICIPALITY", "lv", ""),),
        "LV-016": (Entity("Bauskas novads", "LV-016", "MUNICIPALITY", "lv", ""),),
        "LV-022": (Entity("Cēsu novads", "LV-022", "MUNICIPALITY", "lv", ""),),
        "LV-026": (Entity("Dobeles novads", "LV-026", "MUNICIPALITY", "lv", ""),),
        "LV-033": (Entity("Gulbenes novads", "LV-033", "MUNICIPALITY", "lv", ""),),
        "LV-041": (Entity("Jelgavas novads", "LV-041", "MUNICIPALITY", "lv", ""),),
        "LV-042": (Entity("Jēkabpils novads", "LV-042", "MUNICIPALITY", "lv", ""),),
        "LV-047": (Entity("Krāslavas novads", "LV-047", "MUNICIPALITY", "lv", ""),),
        "LV-050": (Entity("Kuldīgas novads", "LV-050", "MUNICIPALITY", "lv", ""),),
        "LV-052": (Entity("Ķekavas novads", "LV-052", "MUNICIPALITY", "lv", ""),),
        "LV-054": (Entity("Limbažu novads", "LV-054", "MUNICIPALITY", "lv", ""),),
        "LV-056": (Entity("Līvānu novads", "LV-056", "MUNICIPALITY", "lv", ""),),
        "LV-058": (Entity("Ludzas novads", "LV-058", "MUNICIPALITY", "lv", ""),),
        "LV-059": (Entity("Madonas novads", "LV-059", "MUNICIPALITY", "lv", ""),),
        "LV-062": (Entity("Mārupes novads", "LV-062", "MUNICIPALITY", "lv", ""),),
        "LV-067": (Entity("Ogres novads", "LV-067", "MUNICIPALITY", "lv", ""),),
        "LV-068": (Entity("Olaines novads", "LV-068", "MUNICIPALITY", "lv", ""),),
        "LV-073": (Entity("Preiļu novads", "LV-073", "MUNICIPALITY", "lv", ""),),
        "LV-077": (Entity("Rēzeknes novads", "LV-077", "MUNICIPALITY", "lv", ""),),
        "LV-080": (Entity("Ropažu novads", "LV-080", "MUNICIPALITY", "lv", ""),),
        "LV-087": (Entity("Salaspils novads", "LV-087", "MUNICIPALITY", "lv", ""),),
        "LV-088": (Entity("Saldus novads", "LV-088", "MUNICIPALITY", "lv", ""),),
        "LV-089": (Entity("Saulkrastu novads", "LV-089", "MUNICIPALITY", "lv", ""),),
        "LV-091": (Entity("Siguldas novads", "LV-091", "MUNICIPALITY", "lv", ""),),
        "LV-094": (Entity("Smiltenes novads", "LV-094", "MUNICIPALITY", "lv", ""),),
        "LV-097": (Entity("Talsu novads", "LV-097", "MUNICIPALITY", "lv", ""),),
        "LV-099": (Entity("Tukuma novads", "LV-099", "MUNICIPALITY", "lv", ""),),
        "LV-101": (Entity("Valkas novads", "LV-101", "MUNICIPALITY", "lv", ""),),
        "LV-102": (Entity("Varakļānu novads", "LV-102", "MUNICIPALITY", "lv", ""),),
        "LV-106": (Entity("Ventspils novads", "LV-106", "MUNICIPALITY", "lv", ""),),
        "LV-111": (Entity("Augšdaugavas novads", "LV-111", "MUNICIPALITY", "lv", ""),),
        "LV-112": (Entity("Dienvidkurzemes Novads", "LV-112", "MUNICIPALITY", "lv", ""),),
        "LV-113": (Entity("Valmieras Novads", "LV-113", "MUNICIPALITY", "lv", ""),),
        "LV-DGV": (Entity("Daugavpils", "LV-DGV", "STATE CITY", "lv", ""),),
        "LV-JEL": (Entity("Jelgava", "LV-JEL", "STATE CITY", "lv", ""),),
        "LV-JUR": (Entity("Jūrmala", "LV-JUR", "STATE CITY", "lv", ""),),
        "LV-LPX": (Entity("Liepāja", "LV-LPX", "STATE CITY", "lv", ""),),
        "LV-REZ": (Entity("Rēzekne", "LV-REZ", "STATE CITY", "lv", ""),),
        "LV-RIX": (Entity("Rīga", "LV-RIX", "STATE CITY", "lv", ""),),
        "LV-VEN": (Entity("Ventspils", "LV-VEN", "STATE CITY", "lv", ""),),
    }
