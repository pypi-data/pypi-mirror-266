"""ISO 3166-2 NI standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:NI
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "NI-AN": (Entity("Costa Caribe Norte", "NI-AN", "AUTONOMOUS REGION", "es", ""),),
        "NI-AS": (Entity("Costa Caribe Sur", "NI-AS", "AUTONOMOUS REGION", "es", ""),),
        "NI-BO": (Entity("Boaco", "NI-BO", "DEPARTMENT", "es", ""),),
        "NI-CA": (Entity("Carazo", "NI-CA", "DEPARTMENT", "es", ""),),
        "NI-CI": (Entity("Chinandega", "NI-CI", "DEPARTMENT", "es", ""),),
        "NI-CO": (Entity("Chontales", "NI-CO", "DEPARTMENT", "es", ""),),
        "NI-ES": (Entity("Estelí", "NI-ES", "DEPARTMENT", "es", ""),),
        "NI-GR": (Entity("Granada", "NI-GR", "DEPARTMENT", "es", ""),),
        "NI-JI": (Entity("Jinotega", "NI-JI", "DEPARTMENT", "es", ""),),
        "NI-LE": (Entity("León", "NI-LE", "DEPARTMENT", "es", ""),),
        "NI-MD": (Entity("Madriz", "NI-MD", "DEPARTMENT", "es", ""),),
        "NI-MN": (Entity("Managua", "NI-MN", "DEPARTMENT", "es", ""),),
        "NI-MS": (Entity("Masaya", "NI-MS", "DEPARTMENT", "es", ""),),
        "NI-MT": (Entity("Matagalpa", "NI-MT", "DEPARTMENT", "es", ""),),
        "NI-NS": (Entity("Nueva Segovia", "NI-NS", "DEPARTMENT", "es", ""),),
        "NI-RI": (Entity("Rivas", "NI-RI", "DEPARTMENT", "es", ""),),
        "NI-SJ": (Entity("Río San Juan", "NI-SJ", "DEPARTMENT", "es", ""),),
    }
