"""ISO 3166-2 PY standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:PY
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "PY-1": (Entity("Concepción", "PY-1", "DEPARTMENT", "es", ""),),
        "PY-10": (Entity("Alto Paraná", "PY-10", "DEPARTMENT", "es", ""),),
        "PY-11": (Entity("Central", "PY-11", "DEPARTMENT", "es", ""),),
        "PY-12": (Entity("Ñeembucú", "PY-12", "DEPARTMENT", "es", ""),),
        "PY-13": (Entity("Amambay", "PY-13", "DEPARTMENT", "es", ""),),
        "PY-14": (Entity("Canindeyú", "PY-14", "DEPARTMENT", "es", ""),),
        "PY-15": (Entity("Presidente Hayes", "PY-15", "DEPARTMENT", "es", ""),),
        "PY-16": (Entity("Alto Paraguay", "PY-16", "DEPARTMENT", "es", ""),),
        "PY-19": (Entity("Boquerón", "PY-19", "DEPARTMENT", "es", ""),),
        "PY-2": (Entity("San Pedro", "PY-2", "DEPARTMENT", "es", ""),),
        "PY-3": (Entity("Cordillera", "PY-3", "DEPARTMENT", "es", ""),),
        "PY-4": (Entity("Guairá", "PY-4", "DEPARTMENT", "es", ""),),
        "PY-5": (Entity("Caaguazú", "PY-5", "DEPARTMENT", "es", ""),),
        "PY-6": (Entity("Caazapá", "PY-6", "DEPARTMENT", "es", ""),),
        "PY-7": (Entity("Itapúa", "PY-7", "DEPARTMENT", "es", ""),),
        "PY-8": (Entity("Misiones", "PY-8", "DEPARTMENT", "es", ""),),
        "PY-9": (Entity("Paraguarí", "PY-9", "DEPARTMENT", "es", ""),),
        "PY-ASU": (Entity("Asunción", "PY-ASU", "CAPITAL", "es", ""),),
    }
