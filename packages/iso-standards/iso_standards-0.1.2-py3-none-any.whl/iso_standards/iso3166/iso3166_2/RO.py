"""ISO 3166-2 RO standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:RO
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "RO-AB": (Entity("Alba", "RO-AB", "DEPARTMENT", "ro", ""),),
        "RO-AG": (Entity("Argeș", "RO-AG", "DEPARTMENT", "ro", ""),),
        "RO-AR": (Entity("Arad", "RO-AR", "DEPARTMENT", "ro", ""),),
        "RO-B": (Entity("București", "RO-B", "MUNICIPALITY", "ro", ""),),
        "RO-BC": (Entity("Bacău", "RO-BC", "DEPARTMENT", "ro", ""),),
        "RO-BH": (Entity("Bihor", "RO-BH", "DEPARTMENT", "ro", ""),),
        "RO-BN": (Entity("Bistrița-Năsăud", "RO-BN", "DEPARTMENT", "ro", ""),),
        "RO-BR": (Entity("Brăila", "RO-BR", "DEPARTMENT", "ro", ""),),
        "RO-BT": (Entity("Botoșani", "RO-BT", "DEPARTMENT", "ro", ""),),
        "RO-BV": (Entity("Brașov", "RO-BV", "DEPARTMENT", "ro", ""),),
        "RO-BZ": (Entity("Buzău", "RO-BZ", "DEPARTMENT", "ro", ""),),
        "RO-CJ": (Entity("Cluj", "RO-CJ", "DEPARTMENT", "ro", ""),),
        "RO-CL": (Entity("Călărași", "RO-CL", "DEPARTMENT", "ro", ""),),
        "RO-CS": (Entity("Caraș-Severin", "RO-CS", "DEPARTMENT", "ro", ""),),
        "RO-CT": (Entity("Constanța", "RO-CT", "DEPARTMENT", "ro", ""),),
        "RO-CV": (Entity("Covasna", "RO-CV", "DEPARTMENT", "ro", ""),),
        "RO-DB": (Entity("Dâmbovița", "RO-DB", "DEPARTMENT", "ro", ""),),
        "RO-DJ": (Entity("Dolj", "RO-DJ", "DEPARTMENT", "ro", ""),),
        "RO-GJ": (Entity("Gorj", "RO-GJ", "DEPARTMENT", "ro", ""),),
        "RO-GL": (Entity("Galați", "RO-GL", "DEPARTMENT", "ro", ""),),
        "RO-GR": (Entity("Giurgiu", "RO-GR", "DEPARTMENT", "ro", ""),),
        "RO-HD": (Entity("Hunedoara", "RO-HD", "DEPARTMENT", "ro", ""),),
        "RO-HR": (Entity("Harghita", "RO-HR", "DEPARTMENT", "ro", ""),),
        "RO-IF": (Entity("Ilfov", "RO-IF", "DEPARTMENT", "ro", ""),),
        "RO-IL": (Entity("Ialomița", "RO-IL", "DEPARTMENT", "ro", ""),),
        "RO-IS": (Entity("Iași", "RO-IS", "DEPARTMENT", "ro", ""),),
        "RO-MH": (Entity("Mehedinți", "RO-MH", "DEPARTMENT", "ro", ""),),
        "RO-MM": (Entity("Maramureș", "RO-MM", "DEPARTMENT", "ro", ""),),
        "RO-MS": (Entity("Mureș", "RO-MS", "DEPARTMENT", "ro", ""),),
        "RO-NT": (Entity("Neamț", "RO-NT", "DEPARTMENT", "ro", ""),),
        "RO-OT": (Entity("Olt", "RO-OT", "DEPARTMENT", "ro", ""),),
        "RO-PH": (Entity("Prahova", "RO-PH", "DEPARTMENT", "ro", ""),),
        "RO-SB": (Entity("Sibiu", "RO-SB", "DEPARTMENT", "ro", ""),),
        "RO-SJ": (Entity("Sălaj", "RO-SJ", "DEPARTMENT", "ro", ""),),
        "RO-SM": (Entity("Satu Mare", "RO-SM", "DEPARTMENT", "ro", ""),),
        "RO-SV": (Entity("Suceava", "RO-SV", "DEPARTMENT", "ro", ""),),
        "RO-TL": (Entity("Tulcea", "RO-TL", "DEPARTMENT", "ro", ""),),
        "RO-TM": (Entity("Timiș", "RO-TM", "DEPARTMENT", "ro", ""),),
        "RO-TR": (Entity("Teleorman", "RO-TR", "DEPARTMENT", "ro", ""),),
        "RO-VL": (Entity("Vâlcea", "RO-VL", "DEPARTMENT", "ro", ""),),
        "RO-VN": (Entity("Vrancea", "RO-VN", "DEPARTMENT", "ro", ""),),
        "RO-VS": (Entity("Vaslui", "RO-VS", "DEPARTMENT", "ro", ""),),
    }
