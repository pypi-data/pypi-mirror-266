"""ISO 3166-2 GY standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:GY
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "GY-BA": (Entity("Barima-Waini", "GY-BA", "REGION", "en", ""),),
        "GY-CU": (Entity("Cuyuni-Mazaruni", "GY-CU", "REGION", "en", ""),),
        "GY-DE": (Entity("Demerara-Mahaica", "GY-DE", "REGION", "en", ""),),
        "GY-EB": (Entity("East Berbice-Corentyne", "GY-EB", "REGION", "en", ""),),
        "GY-ES": (Entity("Essequibo Islands-West Demerara", "GY-ES", "REGION", "en", ""),),
        "GY-MA": (Entity("Mahaica-Berbice", "GY-MA", "REGION", "en", ""),),
        "GY-PM": (Entity("Pomeroon-Supenaam", "GY-PM", "REGION", "en", ""),),
        "GY-PT": (Entity("Potaro-Siparuni", "GY-PT", "REGION", "en", ""),),
        "GY-UD": (Entity("Upper Demerara-Berbice", "GY-UD", "REGION", "en", ""),),
        "GY-UT": (Entity("Upper Takutu-Upper Essequibo", "GY-UT", "REGION", "en", ""),),
    }
