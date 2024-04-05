"""ISO 3166-2 CG standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CG
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CG-11": (Entity("Bouenza", "CG-11", "DEPARTMENT", "fr", ""),),
        "CG-12": (Entity("Pool", "CG-12", "DEPARTMENT", "fr", ""),),
        "CG-13": (Entity("Sangha", "CG-13", "DEPARTMENT", "fr", ""),),
        "CG-14": (Entity("Plateaux", "CG-14", "DEPARTMENT", "fr", ""),),
        "CG-15": (Entity("Cuvette-Ouest", "CG-15", "DEPARTMENT", "fr", ""),),
        "CG-16": (Entity("Pointe-Noire", "CG-16", "DEPARTMENT", "fr", ""),),
        "CG-2": (Entity("Lékoumou", "CG-2", "DEPARTMENT", "fr", ""),),
        "CG-5": (Entity("Kouilou", "CG-5", "DEPARTMENT", "fr", ""),),
        "CG-7": (Entity("Likouala", "CG-7", "DEPARTMENT", "fr", ""),),
        "CG-8": (Entity("Cuvette", "CG-8", "DEPARTMENT", "fr", ""),),
        "CG-9": (Entity("Niari", "CG-9", "DEPARTMENT", "fr", ""),),
        "CG-BZV": (Entity("Brazzaville", "CG-BZV", "DEPARTMENT", "fr", ""),),
    }
