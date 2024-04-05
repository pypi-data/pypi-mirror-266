"""ISO 3166-2 SA standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SA
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SA-01": (Entity("Ar Riyāḑ", "SA-01", "REGION", "ar", ""),),
        "SA-02": (Entity("Makkah al Mukarramah", "SA-02", "REGION", "ar", ""),),
        "SA-03": (Entity("Al Madīnah al Munawwarah", "SA-03", "REGION", "ar", ""),),
        "SA-04": (Entity("Ash Sharqīyah", "SA-04", "REGION", "ar", ""),),
        "SA-05": (Entity("Al Qaşīm", "SA-05", "REGION", "ar", ""),),
        "SA-06": (Entity("Ḩā'il", "SA-06", "REGION", "ar", ""),),
        "SA-07": (Entity("Tabūk", "SA-07", "REGION", "ar", ""),),
        "SA-08": (Entity("Al Ḩudūd ash Shamālīyah", "SA-08", "REGION", "ar", ""),),
        "SA-09": (Entity("Jāzān", "SA-09", "REGION", "ar", ""),),
        "SA-10": (Entity("Najrān", "SA-10", "REGION", "ar", ""),),
        "SA-11": (Entity("Al Bāḩah", "SA-11", "REGION", "ar", ""),),
        "SA-12": (Entity("Al Jawf", "SA-12", "REGION", "ar", ""),),
        "SA-14": (Entity("'Asīr", "SA-14", "REGION", "ar", ""),),
    }
