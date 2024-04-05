"""ISO 3166-2 AR standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:AR
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "AR-A": (Entity("Salta", "AR-A", "PROVINCE", "es", ""),),
        "AR-B": (Entity("Buenos Aires", "AR-B", "PROVINCE", "es", ""),),
        "AR-C": (Entity("Ciudad Autónoma de Buenos Aires", "AR-C", "CITY", "es", ""),),
        "AR-D": (Entity("San Luis", "AR-D", "PROVINCE", "es", ""),),
        "AR-E": (Entity("Entre Ríos", "AR-E", "PROVINCE", "es", ""),),
        "AR-F": (Entity("La Rioja", "AR-F", "PROVINCE", "es", ""),),
        "AR-G": (Entity("Santiago del Estero", "AR-G", "PROVINCE", "es", ""),),
        "AR-H": (Entity("Chaco", "AR-H", "PROVINCE", "es", ""),),
        "AR-J": (Entity("San Juan", "AR-J", "PROVINCE", "es", ""),),
        "AR-K": (Entity("Catamarca", "AR-K", "PROVINCE", "es", ""),),
        "AR-L": (Entity("La Pampa", "AR-L", "PROVINCE", "es", ""),),
        "AR-M": (Entity("Mendoza", "AR-M", "PROVINCE", "es", ""),),
        "AR-N": (Entity("Misiones", "AR-N", "PROVINCE", "es", ""),),
        "AR-P": (Entity("Formosa", "AR-P", "PROVINCE", "es", ""),),
        "AR-Q": (Entity("Neuquén", "AR-Q", "PROVINCE", "es", ""),),
        "AR-R": (Entity("Río Negro", "AR-R", "PROVINCE", "es", ""),),
        "AR-S": (Entity("Santa Fe", "AR-S", "PROVINCE", "es", ""),),
        "AR-T": (Entity("Tucumán", "AR-T", "PROVINCE", "es", ""),),
        "AR-U": (Entity("Chubut", "AR-U", "PROVINCE", "es", ""),),
        "AR-V": (Entity("Tierra del Fuego", "AR-V", "PROVINCE", "es", ""),),
        "AR-W": (Entity("Corrientes", "AR-W", "PROVINCE", "es", ""),),
        "AR-X": (Entity("Córdoba", "AR-X", "PROVINCE", "es", ""),),
        "AR-Y": (Entity("Jujuy", "AR-Y", "PROVINCE", "es", ""),),
        "AR-Z": (Entity("Santa Cruz", "AR-Z", "PROVINCE", "es", ""),),
    }
