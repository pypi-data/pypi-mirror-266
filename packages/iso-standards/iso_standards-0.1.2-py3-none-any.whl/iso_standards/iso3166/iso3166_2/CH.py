"""ISO 3166-2 CH standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CH
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CH-AG": (Entity("Aargau", "CH-AG", "CANTON", "de", ""),),
        "CH-AI": (Entity("Appenzell Innerrhoden", "CH-AI", "CANTON", "de", ""),),
        "CH-AR": (Entity("Appenzell Ausserrhoden", "CH-AR", "CANTON", "de", ""),),
        "CH-BE": (
            Entity("Bern", "CH-BE", "CANTON", "de", ""),
            Entity("Berne", "CH-BE", "CANTON", "fr", ""),
        ),
        "CH-BL": (Entity("Basel-Landschaft", "CH-BL", "CANTON", "de", ""),),
        "CH-BS": (Entity("Basel-Stadt", "CH-BS", "CANTON", "de", ""),),
        "CH-FR": (
            Entity("Freiburg", "CH-FR", "CANTON", "de", ""),
            Entity("Fribourg", "CH-FR", "CANTON", "fr", ""),
        ),
        "CH-GE": (Entity("Genève", "CH-GE", "CANTON", "fr", ""),),
        "CH-GL": (Entity("Glarus", "CH-GL", "CANTON", "de", ""),),
        "CH-GR": (
            Entity("Graubünden", "CH-GR", "CANTON", "de", ""),
            Entity("Grigioni", "CH-GR", "CANTON", "it", ""),
            Entity("Grischun", "CH-GR", "CANTON", "rm", ""),
        ),
        "CH-JU": (Entity("Jura", "CH-JU", "CANTON", "fr", ""),),
        "CH-LU": (Entity("Luzern", "CH-LU", "CANTON", "de", ""),),
        "CH-NE": (Entity("Neuchâtel", "CH-NE", "CANTON", "fr", ""),),
        "CH-NW": (Entity("Nidwalden", "CH-NW", "CANTON", "de", ""),),
        "CH-OW": (Entity("Obwalden", "CH-OW", "CANTON", "de", ""),),
        "CH-SG": (Entity("Sankt Gallen", "CH-SG", "CANTON", "de", ""),),
        "CH-SH": (Entity("Schaffhausen", "CH-SH", "CANTON", "de", ""),),
        "CH-SO": (Entity("Solothurn", "CH-SO", "CANTON", "de", ""),),
        "CH-SZ": (Entity("Schwyz", "CH-SZ", "CANTON", "de", ""),),
        "CH-TG": (Entity("Thurgau", "CH-TG", "CANTON", "de", ""),),
        "CH-TI": (Entity("Ticino", "CH-TI", "CANTON", "it", ""),),
        "CH-UR": (Entity("Uri", "CH-UR", "CANTON", "de", ""),),
        "CH-VD": (Entity("Vaud", "CH-VD", "CANTON", "fr", ""),),
        "CH-VS": (
            Entity("Valais", "CH-VS", "CANTON", "fr", ""),
            Entity("Wallis", "CH-VS", "CANTON", "de", ""),
        ),
        "CH-ZG": (Entity("Zug", "CH-ZG", "CANTON", "de", ""),),
        "CH-ZH": (Entity("Zürich", "CH-ZH", "CANTON", "de", ""),),
    }
