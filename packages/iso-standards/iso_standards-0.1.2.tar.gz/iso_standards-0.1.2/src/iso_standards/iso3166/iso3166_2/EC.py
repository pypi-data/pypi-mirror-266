"""ISO 3166-2 EC standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:EC
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "EC-A": (Entity("Azuay", "EC-A", "PROVINCE", "es", ""),),
        "EC-B": (Entity("Bolívar", "EC-B", "PROVINCE", "es", ""),),
        "EC-C": (Entity("Carchi", "EC-C", "PROVINCE", "es", ""),),
        "EC-D": (Entity("Orellana", "EC-D", "PROVINCE", "es", ""),),
        "EC-E": (Entity("Esmeraldas", "EC-E", "PROVINCE", "es", ""),),
        "EC-F": (Entity("Cañar", "EC-F", "PROVINCE", "es", ""),),
        "EC-G": (Entity("Guayas", "EC-G", "PROVINCE", "es", ""),),
        "EC-H": (Entity("Chimborazo", "EC-H", "PROVINCE", "es", ""),),
        "EC-I": (Entity("Imbabura", "EC-I", "PROVINCE", "es", ""),),
        "EC-L": (Entity("Loja", "EC-L", "PROVINCE", "es", ""),),
        "EC-M": (Entity("Manabí", "EC-M", "PROVINCE", "es", ""),),
        "EC-N": (Entity("Napo", "EC-N", "PROVINCE", "es", ""),),
        "EC-O": (Entity("El Oro", "EC-O", "PROVINCE", "es", ""),),
        "EC-P": (Entity("Pichincha", "EC-P", "PROVINCE", "es", ""),),
        "EC-R": (Entity("Los Ríos", "EC-R", "PROVINCE", "es", ""),),
        "EC-S": (Entity("Morona Santiago", "EC-S", "PROVINCE", "es", ""),),
        "EC-SD": (Entity("Santo Domingo de los Tsáchilas", "EC-SD", "PROVINCE", "es", ""),),
        "EC-SE": (Entity("Santa Elena", "EC-SE", "PROVINCE", "es", ""),),
        "EC-T": (Entity("Tungurahua", "EC-T", "PROVINCE", "es", ""),),
        "EC-U": (Entity("Sucumbíos", "EC-U", "PROVINCE", "es", ""),),
        "EC-W": (Entity("Galápagos", "EC-W", "PROVINCE", "es", ""),),
        "EC-X": (Entity("Cotopaxi", "EC-X", "PROVINCE", "es", ""),),
        "EC-Y": (Entity("Pastaza", "EC-Y", "PROVINCE", "es", ""),),
        "EC-Z": (Entity("Zamora Chinchipe", "EC-Z", "PROVINCE", "es", ""),),
    }
