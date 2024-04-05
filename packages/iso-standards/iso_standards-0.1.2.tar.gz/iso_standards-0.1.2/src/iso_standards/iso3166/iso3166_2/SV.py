"""ISO 3166-2 SV standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SV
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SV-AH": (Entity("Ahuachapán", "SV-AH", "DEPARTMENT", "es", ""),),
        "SV-CA": (Entity("Cabañas", "SV-CA", "DEPARTMENT", "es", ""),),
        "SV-CH": (Entity("Chalatenango", "SV-CH", "DEPARTMENT", "es", ""),),
        "SV-CU": (Entity("Cuscatlán", "SV-CU", "DEPARTMENT", "es", ""),),
        "SV-LI": (Entity("La Libertad", "SV-LI", "DEPARTMENT", "es", ""),),
        "SV-MO": (Entity("Morazán", "SV-MO", "DEPARTMENT", "es", ""),),
        "SV-PA": (Entity("La Paz", "SV-PA", "DEPARTMENT", "es", ""),),
        "SV-SA": (Entity("Santa Ana", "SV-SA", "DEPARTMENT", "es", ""),),
        "SV-SM": (Entity("San Miguel", "SV-SM", "DEPARTMENT", "es", ""),),
        "SV-SO": (Entity("Sonsonate", "SV-SO", "DEPARTMENT", "es", ""),),
        "SV-SS": (Entity("San Salvador", "SV-SS", "DEPARTMENT", "es", ""),),
        "SV-SV": (Entity("San Vicente", "SV-SV", "DEPARTMENT", "es", ""),),
        "SV-UN": (Entity("La Unión", "SV-UN", "DEPARTMENT", "es", ""),),
        "SV-US": (Entity("Usulután", "SV-US", "DEPARTMENT", "es", ""),),
    }
