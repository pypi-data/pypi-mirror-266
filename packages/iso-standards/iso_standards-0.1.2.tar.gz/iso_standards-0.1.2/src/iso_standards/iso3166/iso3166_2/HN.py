"""ISO 3166-2 HN standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:HN
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "HN-AT": (Entity("Atlántida", "HN-AT", "DEPARTMENT", "es", ""),),
        "HN-CH": (Entity("Choluteca", "HN-CH", "DEPARTMENT", "es", ""),),
        "HN-CL": (Entity("Colón", "HN-CL", "DEPARTMENT", "es", ""),),
        "HN-CM": (Entity("Comayagua", "HN-CM", "DEPARTMENT", "es", ""),),
        "HN-CP": (Entity("Copán", "HN-CP", "DEPARTMENT", "es", ""),),
        "HN-CR": (Entity("Cortés", "HN-CR", "DEPARTMENT", "es", ""),),
        "HN-EP": (Entity("El Paraíso", "HN-EP", "DEPARTMENT", "es", ""),),
        "HN-FM": (Entity("Francisco Morazán", "HN-FM", "DEPARTMENT", "es", ""),),
        "HN-GD": (Entity("Gracias a Dios", "HN-GD", "DEPARTMENT", "es", ""),),
        "HN-IB": (Entity("Islas de la Bahía", "HN-IB", "DEPARTMENT", "es", ""),),
        "HN-IN": (Entity("Intibucá", "HN-IN", "DEPARTMENT", "es", ""),),
        "HN-LE": (Entity("Lempira", "HN-LE", "DEPARTMENT", "es", ""),),
        "HN-LP": (Entity("La Paz", "HN-LP", "DEPARTMENT", "es", ""),),
        "HN-OC": (Entity("Ocotepeque", "HN-OC", "DEPARTMENT", "es", ""),),
        "HN-OL": (Entity("Olancho", "HN-OL", "DEPARTMENT", "es", ""),),
        "HN-SB": (Entity("Santa Bárbara", "HN-SB", "DEPARTMENT", "es", ""),),
        "HN-VA": (Entity("Valle", "HN-VA", "DEPARTMENT", "es", ""),),
        "HN-YO": (Entity("Yoro", "HN-YO", "DEPARTMENT", "es", ""),),
    }
