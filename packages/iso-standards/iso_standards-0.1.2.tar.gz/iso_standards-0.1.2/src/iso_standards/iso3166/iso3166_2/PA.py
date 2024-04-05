"""ISO 3166-2 PA standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:PA
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "PA-1": (Entity("Bocas del Toro", "PA-1", "PROVINCE", "es", ""),),
        "PA-10": (Entity("Panamá Oeste", "PA-10", "PROVINCE", "es", ""),),
        "PA-2": (Entity("Coclé", "PA-2", "PROVINCE", "es", ""),),
        "PA-3": (Entity("Colón", "PA-3", "PROVINCE", "es", ""),),
        "PA-4": (Entity("Chiriquí", "PA-4", "PROVINCE", "es", ""),),
        "PA-5": (Entity("Darién", "PA-5", "PROVINCE", "es", ""),),
        "PA-6": (Entity("Herrera", "PA-6", "PROVINCE", "es", ""),),
        "PA-7": (Entity("Los Santos", "PA-7", "PROVINCE", "es", ""),),
        "PA-8": (Entity("Panamá", "PA-8", "PROVINCE", "es", ""),),
        "PA-9": (Entity("Veraguas", "PA-9", "PROVINCE", "es", ""),),
        "PA-EM": (Entity("Emberá", "PA-EM", "INDIGENOUS REGION", "es", ""),),
        "PA-KY": (Entity("Guna Yala", "PA-KY", "INDIGENOUS REGION", "es", ""),),
        "PA-NB": (Entity("Ngäbe-Buglé", "PA-NB", "INDIGENOUS REGION", "es", ""),),
        "PA-NT": (Entity("Naso Tjër Di", "PA-NT", "INDIGENOUS REGION", "es", ""),),
    }
