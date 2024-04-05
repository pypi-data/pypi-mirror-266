"""ISO 3166-2 CU standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CU
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CU-01": (Entity("Pinar del Río", "CU-01", "PROVINCE", "es", ""),),
        "CU-03": (Entity("La Habana", "CU-03", "PROVINCE", "es", ""),),
        "CU-04": (Entity("Matanzas", "CU-04", "PROVINCE", "es", ""),),
        "CU-05": (Entity("Villa Clara", "CU-05", "PROVINCE", "es", ""),),
        "CU-06": (Entity("Cienfuegos", "CU-06", "PROVINCE", "es", ""),),
        "CU-07": (Entity("Sancti Spíritus", "CU-07", "PROVINCE", "es", ""),),
        "CU-08": (Entity("Ciego de Ávila", "CU-08", "PROVINCE", "es", ""),),
        "CU-09": (Entity("Camagüey", "CU-09", "PROVINCE", "es", ""),),
        "CU-10": (Entity("Las Tunas", "CU-10", "PROVINCE", "es", ""),),
        "CU-11": (Entity("Holguín", "CU-11", "PROVINCE", "es", ""),),
        "CU-12": (Entity("Granma", "CU-12", "PROVINCE", "es", ""),),
        "CU-13": (Entity("Santiago de Cuba", "CU-13", "PROVINCE", "es", ""),),
        "CU-14": (Entity("Guantánamo", "CU-14", "PROVINCE", "es", ""),),
        "CU-15": (Entity("Artemisa", "CU-15", "PROVINCE", "es", ""),),
        "CU-16": (Entity("Mayabeque", "CU-16", "PROVINCE", "es", ""),),
        "CU-99": (Entity("Isla de la Juventud", "CU-99", "SPECIAL MUNICIPALITY", "es", ""),),
    }
