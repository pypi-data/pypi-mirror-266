"""ISO 3166-2 PT standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:PT
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "PT-01": (Entity("Aveiro", "PT-01", "DISTRICT", "pt", ""),),
        "PT-02": (Entity("Beja", "PT-02", "DISTRICT", "pt", ""),),
        "PT-03": (Entity("Braga", "PT-03", "DISTRICT", "pt", ""),),
        "PT-04": (Entity("Bragança", "PT-04", "DISTRICT", "pt", ""),),
        "PT-05": (Entity("Castelo Branco", "PT-05", "DISTRICT", "pt", ""),),
        "PT-06": (Entity("Coimbra", "PT-06", "DISTRICT", "pt", ""),),
        "PT-07": (Entity("Évora", "PT-07", "DISTRICT", "pt", ""),),
        "PT-08": (Entity("Faro", "PT-08", "DISTRICT", "pt", ""),),
        "PT-09": (Entity("Guarda", "PT-09", "DISTRICT", "pt", ""),),
        "PT-10": (Entity("Leiria", "PT-10", "DISTRICT", "pt", ""),),
        "PT-11": (Entity("Lisboa", "PT-11", "DISTRICT", "pt", ""),),
        "PT-12": (Entity("Portalegre", "PT-12", "DISTRICT", "pt", ""),),
        "PT-13": (Entity("Porto", "PT-13", "DISTRICT", "pt", ""),),
        "PT-14": (Entity("Santarém", "PT-14", "DISTRICT", "pt", ""),),
        "PT-15": (Entity("Setúbal", "PT-15", "DISTRICT", "pt", ""),),
        "PT-16": (Entity("Viana do Castelo", "PT-16", "DISTRICT", "pt", ""),),
        "PT-17": (Entity("Vila Real", "PT-17", "DISTRICT", "pt", ""),),
        "PT-18": (Entity("Viseu", "PT-18", "DISTRICT", "pt", ""),),
        "PT-20": (Entity("Região Autónoma dos Açores", "PT-20", "AUTONOMOUS REGION", "pt", ""),),
        "PT-30": (Entity("Região Autónoma da Madeira", "PT-30", "AUTONOMOUS REGION", "pt", ""),),
    }
