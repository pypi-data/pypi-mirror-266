"""ISO 3166-2 LA standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:LA
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "LA-AT": (Entity("Attapu", "LA-AT", "PROVINCE", "lo", ""),),
        "LA-BK": (Entity("Bokèo", "LA-BK", "PROVINCE", "lo", ""),),
        "LA-BL": (Entity("Bolikhamxai", "LA-BL", "PROVINCE", "lo", ""),),
        "LA-CH": (Entity("Champasak", "LA-CH", "PROVINCE", "lo", ""),),
        "LA-HO": (Entity("Houaphan", "LA-HO", "PROVINCE", "lo", ""),),
        "LA-KH": (Entity("Khammouan", "LA-KH", "PROVINCE", "lo", ""),),
        "LA-LM": (Entity("Louang Namtha", "LA-LM", "PROVINCE", "lo", ""),),
        "LA-LP": (Entity("Louangphabang", "LA-LP", "PROVINCE", "lo", ""),),
        "LA-OU": (Entity("Oudômxai", "LA-OU", "PROVINCE", "lo", ""),),
        "LA-PH": (Entity("Phôngsali", "LA-PH", "PROVINCE", "lo", ""),),
        "LA-SL": (Entity("Salavan", "LA-SL", "PROVINCE", "lo", ""),),
        "LA-SV": (Entity("Savannakhét", "LA-SV", "PROVINCE", "lo", ""),),
        "LA-VI": (Entity("Viangchan", "LA-VI", "PROVINCE", "lo", ""),),
        "LA-VT": (Entity("Viangchan", "LA-VT", "PREFECTURE", "lo", ""),),
        "LA-XA": (Entity("Xaignabouli", "LA-XA", "PROVINCE", "lo", ""),),
        "LA-XE": (Entity("Xékong", "LA-XE", "PROVINCE", "lo", ""),),
        "LA-XI": (Entity("Xiangkhouang", "LA-XI", "PROVINCE", "lo", ""),),
        "LA-XS": (Entity("Xaisômboun", "LA-XS", "PROVINCE", "lo", ""),),
    }
