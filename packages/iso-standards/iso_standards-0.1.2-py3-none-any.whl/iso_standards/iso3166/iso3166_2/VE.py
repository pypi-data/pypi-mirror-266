"""ISO 3166-2 VE standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:VE
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "VE-A": (Entity("Distrito Capital", "VE-A", "CAPITAL DISTRICT", "es", ""),),
        "VE-B": (Entity("Anzoátegui", "VE-B", "STATE", "es", ""),),
        "VE-C": (Entity("Apure", "VE-C", "STATE", "es", ""),),
        "VE-D": (Entity("Aragua", "VE-D", "STATE", "es", ""),),
        "VE-E": (Entity("Barinas", "VE-E", "STATE", "es", ""),),
        "VE-F": (Entity("Bolívar", "VE-F", "STATE", "es", ""),),
        "VE-G": (Entity("Carabobo", "VE-G", "STATE", "es", ""),),
        "VE-H": (Entity("Cojedes", "VE-H", "STATE", "es", ""),),
        "VE-I": (Entity("Falcón", "VE-I", "STATE", "es", ""),),
        "VE-J": (Entity("Guárico", "VE-J", "STATE", "es", ""),),
        "VE-K": (Entity("Lara", "VE-K", "STATE", "es", ""),),
        "VE-L": (Entity("Mérida", "VE-L", "STATE", "es", ""),),
        "VE-M": (Entity("Miranda", "VE-M", "STATE", "es", ""),),
        "VE-N": (Entity("Monagas", "VE-N", "STATE", "es", ""),),
        "VE-O": (Entity("Nueva Esparta", "VE-O", "STATE", "es", ""),),
        "VE-P": (Entity("Portuguesa", "VE-P", "STATE", "es", ""),),
        "VE-R": (Entity("Sucre", "VE-R", "STATE", "es", ""),),
        "VE-S": (Entity("Táchira", "VE-S", "STATE", "es", ""),),
        "VE-T": (Entity("Trujillo", "VE-T", "STATE", "es", ""),),
        "VE-U": (Entity("Yaracuy", "VE-U", "STATE", "es", ""),),
        "VE-V": (Entity("Zulia", "VE-V", "STATE", "es", ""),),
        "VE-W": (Entity("Dependencias Federales", "VE-W", "FEDERAL DEPENDENCY", "es", ""),),
        "VE-X": (Entity("La Guaira", "VE-X", "STATE", "es", ""),),
        "VE-Y": (Entity("Delta Amacuro", "VE-Y", "STATE", "es", ""),),
        "VE-Z": (Entity("Amazonas", "VE-Z", "STATE", "es", ""),),
    }
