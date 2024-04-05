"""ISO 3166-2 AE standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:AE
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "AE-AJ": (Entity("‘Ajmān", "AE-AJ", "EMIRATE", "ar", ""),),
        "AE-AZ": (Entity("Abū Z̧aby", "AE-AZ", "EMIRATE", "ar", ""),),
        "AE-DU": (Entity("Dubayy", "AE-DU", "EMIRATE", "ar", ""),),
        "AE-FU": (Entity("Al Fujayrah", "AE-FU", "EMIRATE", "ar", ""),),
        "AE-RK": (Entity("Ra’s al Khaymah", "AE-RK", "EMIRATE", "ar", ""),),
        "AE-SH": (Entity("Ash Shāriqah", "AE-SH", "EMIRATE", "ar", ""),),
        "AE-UQ": (Entity("Umm al Qaywayn", "AE-UQ", "EMIRATE", "ar", ""),),
    }
