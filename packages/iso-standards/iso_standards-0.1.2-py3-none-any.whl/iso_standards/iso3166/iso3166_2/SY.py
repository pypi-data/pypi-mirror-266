"""ISO 3166-2 SY standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SY
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SY-DI": (Entity("Dimashq", "SY-DI", "PROVINCE", "ar", ""),),
        "SY-DR": (Entity("Dar'ā", "SY-DR", "PROVINCE", "ar", ""),),
        "SY-DY": (Entity("Dayr az Zawr", "SY-DY", "PROVINCE", "ar", ""),),
        "SY-HA": (Entity("Al Ḩasakah", "SY-HA", "PROVINCE", "ar", ""),),
        "SY-HI": (Entity("Ḩimş", "SY-HI", "PROVINCE", "ar", ""),),
        "SY-HL": (Entity("Ḩalab", "SY-HL", "PROVINCE", "ar", ""),),
        "SY-HM": (Entity("Ḩamāh", "SY-HM", "PROVINCE", "ar", ""),),
        "SY-ID": (Entity("Idlib", "SY-ID", "PROVINCE", "ar", ""),),
        "SY-LA": (Entity("Al Lādhiqīyah", "SY-LA", "PROVINCE", "ar", ""),),
        "SY-QU": (Entity("Al Qunayţirah", "SY-QU", "PROVINCE", "ar", ""),),
        "SY-RA": (Entity("Ar Raqqah", "SY-RA", "PROVINCE", "ar", ""),),
        "SY-RD": (Entity("Rīf Dimashq", "SY-RD", "PROVINCE", "ar", ""),),
        "SY-SU": (Entity("As Suwaydā'", "SY-SU", "PROVINCE", "ar", ""),),
        "SY-TA": (Entity("Ţarţūs", "SY-TA", "PROVINCE", "ar", ""),),
    }
