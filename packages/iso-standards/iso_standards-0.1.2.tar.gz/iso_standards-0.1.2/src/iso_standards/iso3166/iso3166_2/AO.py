"""ISO 3166-2 AO standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:AO
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "AO-BGO": (Entity("Bengo", "AO-BGO", "PROVINCE", "pt", ""),),
        "AO-BGU": (Entity("Benguela", "AO-BGU", "PROVINCE", "pt", ""),),
        "AO-BIE": (Entity("Bié", "AO-BIE", "PROVINCE", "pt", ""),),
        "AO-CAB": (Entity("Cabinda", "AO-CAB", "PROVINCE", "pt", ""),),
        "AO-CCU": (Entity("Cuando Cubango", "AO-CCU", "PROVINCE", "pt", ""),),
        "AO-CNN": (Entity("Cunene", "AO-CNN", "PROVINCE", "pt", ""),),
        "AO-CNO": (Entity("Cuanza-Norte", "AO-CNO", "PROVINCE", "pt", ""),),
        "AO-CUS": (Entity("Cuanza-Sul", "AO-CUS", "PROVINCE", "pt", ""),),
        "AO-HUA": (Entity("Huambo", "AO-HUA", "PROVINCE", "pt", ""),),
        "AO-HUI": (Entity("Huíla", "AO-HUI", "PROVINCE", "pt", ""),),
        "AO-LNO": (Entity("Lunda-Norte", "AO-LNO", "PROVINCE", "pt", ""),),
        "AO-LSU": (Entity("Lunda-Sul", "AO-LSU", "PROVINCE", "pt", ""),),
        "AO-LUA": (Entity("Luanda", "AO-LUA", "PROVINCE", "pt", ""),),
        "AO-MAL": (Entity("Malange", "AO-MAL", "PROVINCE", "pt", ""),),
        "AO-MOX": (Entity("Moxico", "AO-MOX", "PROVINCE", "pt", ""),),
        "AO-NAM": (Entity("Namibe", "AO-NAM", "PROVINCE", "pt", ""),),
        "AO-UIG": (Entity("Uíge", "AO-UIG", "PROVINCE", "pt", ""),),
        "AO-ZAI": (Entity("Zaire", "AO-ZAI", "PROVINCE", "pt", ""),),
    }
