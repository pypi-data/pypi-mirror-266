"""ISO 3166-2 GT standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:GT
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "GT-01": (Entity("Guatemala", "GT-01", "DEPARTMENT", "es", ""),),
        "GT-02": (Entity("El Progreso", "GT-02", "DEPARTMENT", "es", ""),),
        "GT-03": (Entity("Sacatepéquez", "GT-03", "DEPARTMENT", "es", ""),),
        "GT-04": (Entity("Chimaltenango", "GT-04", "DEPARTMENT", "es", ""),),
        "GT-05": (Entity("Escuintla", "GT-05", "DEPARTMENT", "es", ""),),
        "GT-06": (Entity("Santa Rosa", "GT-06", "DEPARTMENT", "es", ""),),
        "GT-07": (Entity("Sololá", "GT-07", "DEPARTMENT", "es", ""),),
        "GT-08": (Entity("Totonicapán", "GT-08", "DEPARTMENT", "es", ""),),
        "GT-09": (Entity("Quetzaltenango", "GT-09", "DEPARTMENT", "es", ""),),
        "GT-10": (Entity("Suchitepéquez", "GT-10", "DEPARTMENT", "es", ""),),
        "GT-11": (Entity("Retalhuleu", "GT-11", "DEPARTMENT", "es", ""),),
        "GT-12": (Entity("San Marcos", "GT-12", "DEPARTMENT", "es", ""),),
        "GT-13": (Entity("Huehuetenango", "GT-13", "DEPARTMENT", "es", ""),),
        "GT-14": (Entity("Quiché", "GT-14", "DEPARTMENT", "es", ""),),
        "GT-15": (Entity("Baja Verapaz", "GT-15", "DEPARTMENT", "es", ""),),
        "GT-16": (Entity("Alta Verapaz", "GT-16", "DEPARTMENT", "es", ""),),
        "GT-17": (Entity("Petén", "GT-17", "DEPARTMENT", "es", ""),),
        "GT-18": (Entity("Izabal", "GT-18", "DEPARTMENT", "es", ""),),
        "GT-19": (Entity("Zacapa", "GT-19", "DEPARTMENT", "es", ""),),
        "GT-20": (Entity("Chiquimula", "GT-20", "DEPARTMENT", "es", ""),),
        "GT-21": (Entity("Jalapa", "GT-21", "DEPARTMENT", "es", ""),),
        "GT-22": (Entity("Jutiapa", "GT-22", "DEPARTMENT", "es", ""),),
    }
