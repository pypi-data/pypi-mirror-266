"""ISO 3166-2 CL standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CL
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CL-AI": (
            Entity("Aisén del General Carlos Ibañez del Campo", "CL-AI", "REGION", "es", ""),
        ),
        "CL-AN": (Entity("Antofagasta", "CL-AN", "REGION", "es", ""),),
        "CL-AP": (Entity("Arica y Parinacota", "CL-AP", "REGION", "es", ""),),
        "CL-AR": (Entity("La Araucanía", "CL-AR", "REGION", "es", ""),),
        "CL-AT": (Entity("Atacama", "CL-AT", "REGION", "es", ""),),
        "CL-BI": (Entity("Biobío", "CL-BI", "REGION", "es", ""),),
        "CL-CO": (Entity("Coquimbo", "CL-CO", "REGION", "es", ""),),
        "CL-LI": (Entity("Libertador General Bernardo O'Higgins", "CL-LI", "REGION", "es", ""),),
        "CL-LL": (Entity("Los Lagos", "CL-LL", "REGION", "es", ""),),
        "CL-LR": (Entity("Los Ríos", "CL-LR", "REGION", "es", ""),),
        "CL-MA": (Entity("Magallanes", "CL-MA", "REGION", "es", ""),),
        "CL-ML": (Entity("Maule", "CL-ML", "REGION", "es", ""),),
        "CL-NB": (Entity("Ñuble", "CL-NB", "REGION", "es", ""),),
        "CL-RM": (Entity("Región Metropolitana de Santiago", "CL-RM", "REGION", "es", ""),),
        "CL-TA": (Entity("Tarapacá", "CL-TA", "REGION", "es", ""),),
        "CL-VS": (Entity("Valparaíso", "CL-VS", "REGION", "es", ""),),
    }
