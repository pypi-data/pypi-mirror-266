"""ISO 3166-2 MR standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:MR
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "MR-01": (Entity("Hodh ech Chargui", "MR-01", "REGION", "ar", ""),),
        "MR-02": (Entity("Hodh el Gharbi", "MR-02", "REGION", "ar", ""),),
        "MR-03": (Entity("Assaba", "MR-03", "REGION", "ar", ""),),
        "MR-04": (Entity("Gorgol", "MR-04", "REGION", "ar", ""),),
        "MR-05": (Entity("Brakna", "MR-05", "REGION", "ar", ""),),
        "MR-06": (Entity("Trarza", "MR-06", "REGION", "ar", ""),),
        "MR-07": (Entity("Adrar", "MR-07", "REGION", "ar", ""),),
        "MR-08": (Entity("Dakhlet Nouâdhibou", "MR-08", "REGION", "ar", ""),),
        "MR-09": (Entity("Tagant", "MR-09", "REGION", "ar", ""),),
        "MR-10": (Entity("Guidimaka", "MR-10", "REGION", "ar", ""),),
        "MR-11": (Entity("Tiris Zemmour", "MR-11", "REGION", "ar", ""),),
        "MR-12": (Entity("Inchiri", "MR-12", "REGION", "ar", ""),),
        "MR-13": (
            Entity("Nouakchott Ouest", "MR-13", "REGION", "fr", ""),
            Entity("Nuwākshūţ al Gharbīyah", "MR-13", "REGION", "ar", ""),
        ),
        "MR-14": (
            Entity("Nouakchott Nord", "MR-14", "REGION", "fr", ""),
            Entity("Nuwākshūţ ash Shamālīyah", "MR-14", "REGION", "ar", ""),
        ),
        "MR-15": (
            Entity("Nouakchott Sud", "MR-15", "REGION", "fr", ""),
            Entity("Nuwākshūţ al Janūbīyah", "MR-15", "REGION", "ar", ""),
        ),
    }
