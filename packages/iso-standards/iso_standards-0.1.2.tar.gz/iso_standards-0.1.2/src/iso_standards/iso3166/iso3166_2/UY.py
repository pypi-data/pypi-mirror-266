"""ISO 3166-2 UY standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:UY
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "UY-AR": (Entity("Artigas", "UY-AR", "DEPARTMENT", "es", ""),),
        "UY-CA": (Entity("Canelones", "UY-CA", "DEPARTMENT", "es", ""),),
        "UY-CL": (Entity("Cerro Largo", "UY-CL", "DEPARTMENT", "es", ""),),
        "UY-CO": (Entity("Colonia", "UY-CO", "DEPARTMENT", "es", ""),),
        "UY-DU": (Entity("Durazno", "UY-DU", "DEPARTMENT", "es", ""),),
        "UY-FD": (Entity("Florida", "UY-FD", "DEPARTMENT", "es", ""),),
        "UY-FS": (Entity("Flores", "UY-FS", "DEPARTMENT", "es", ""),),
        "UY-LA": (Entity("Lavalleja", "UY-LA", "DEPARTMENT", "es", ""),),
        "UY-MA": (Entity("Maldonado", "UY-MA", "DEPARTMENT", "es", ""),),
        "UY-MO": (Entity("Montevideo", "UY-MO", "DEPARTMENT", "es", ""),),
        "UY-PA": (Entity("Paysandú", "UY-PA", "DEPARTMENT", "es", ""),),
        "UY-RN": (Entity("Río Negro", "UY-RN", "DEPARTMENT", "es", ""),),
        "UY-RO": (Entity("Rocha", "UY-RO", "DEPARTMENT", "es", ""),),
        "UY-RV": (Entity("Rivera", "UY-RV", "DEPARTMENT", "es", ""),),
        "UY-SA": (Entity("Salto", "UY-SA", "DEPARTMENT", "es", ""),),
        "UY-SJ": (Entity("San José", "UY-SJ", "DEPARTMENT", "es", ""),),
        "UY-SO": (Entity("Soriano", "UY-SO", "DEPARTMENT", "es", ""),),
        "UY-TA": (Entity("Tacuarembó", "UY-TA", "DEPARTMENT", "es", ""),),
        "UY-TT": (Entity("Treinta y Tres", "UY-TT", "DEPARTMENT", "es", ""),),
    }
