"""ISO 3166-2 LY standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:LY
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "LY-BA": (Entity("Banghāzī", "LY-BA", "POPULARATE", "ar", ""),),
        "LY-BU": (Entity("Al Buţnān", "LY-BU", "POPULARATE", "ar", ""),),
        "LY-DR": (Entity("Darnah", "LY-DR", "POPULARATE", "ar", ""),),
        "LY-GT": (Entity("Ghāt", "LY-GT", "POPULARATE", "ar", ""),),
        "LY-JA": (Entity("Al Jabal al Akhḑar", "LY-JA", "POPULARATE", "ar", ""),),
        "LY-JG": (Entity("Al Jabal al Gharbī", "LY-JG", "POPULARATE", "ar", ""),),
        "LY-JI": (Entity("Al Jafārah", "LY-JI", "POPULARATE", "ar", ""),),
        "LY-JU": (Entity("Al Jufrah", "LY-JU", "POPULARATE", "ar", ""),),
        "LY-KF": (Entity("Al Kufrah", "LY-KF", "POPULARATE", "ar", ""),),
        "LY-MB": (Entity("Al Marqab", "LY-MB", "POPULARATE", "ar", ""),),
        "LY-MI": (Entity("Mişrātah", "LY-MI", "POPULARATE", "ar", ""),),
        "LY-MJ": (Entity("Al Marj", "LY-MJ", "POPULARATE", "ar", ""),),
        "LY-MQ": (Entity("Murzuq", "LY-MQ", "POPULARATE", "ar", ""),),
        "LY-NL": (Entity("Nālūt", "LY-NL", "POPULARATE", "ar", ""),),
        "LY-NQ": (Entity("An Nuqāţ al Khams", "LY-NQ", "POPULARATE", "ar", ""),),
        "LY-SB": (Entity("Sabhā", "LY-SB", "POPULARATE", "ar", ""),),
        "LY-SR": (Entity("Surt", "LY-SR", "POPULARATE", "ar", ""),),
        "LY-TB": (Entity("Ţarābulus", "LY-TB", "POPULARATE", "ar", ""),),
        "LY-WA": (Entity("Al Wāḩāt", "LY-WA", "POPULARATE", "ar", ""),),
        "LY-WD": (Entity("Wādī al Ḩayāt", "LY-WD", "POPULARATE", "ar", ""),),
        "LY-WS": (Entity("Wādī ash Shāţi’", "LY-WS", "POPULARATE", "ar", ""),),
        "LY-ZA": (Entity("Az Zāwiyah", "LY-ZA", "POPULARATE", "ar", ""),),
    }
