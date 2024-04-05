"""ISO 3166-2 DE standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:DE
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "DE-BB": (Entity("Brandenburg", "DE-BB", "LAND", "de", ""),),
        "DE-BE": (Entity("Berlin", "DE-BE", "LAND", "de", ""),),
        "DE-BW": (Entity("Baden-Württemberg", "DE-BW", "LAND", "de", ""),),
        "DE-BY": (Entity("Bayern", "DE-BY", "LAND", "de", ""),),
        "DE-HB": (Entity("Bremen", "DE-HB", "LAND", "de", ""),),
        "DE-HE": (Entity("Hessen", "DE-HE", "LAND", "de", ""),),
        "DE-HH": (Entity("Hamburg", "DE-HH", "LAND", "de", ""),),
        "DE-MV": (Entity("Mecklenburg-Vorpommern", "DE-MV", "LAND", "de", ""),),
        "DE-NI": (Entity("Niedersachsen", "DE-NI", "LAND", "de", ""),),
        "DE-NW": (Entity("Nordrhein-Westfalen", "DE-NW", "LAND", "de", ""),),
        "DE-RP": (Entity("Rheinland-Pfalz", "DE-RP", "LAND", "de", ""),),
        "DE-SH": (Entity("Schleswig-Holstein", "DE-SH", "LAND", "de", ""),),
        "DE-SL": (Entity("Saarland", "DE-SL", "LAND", "de", ""),),
        "DE-SN": (Entity("Sachsen", "DE-SN", "LAND", "de", ""),),
        "DE-ST": (Entity("Sachsen-Anhalt", "DE-ST", "LAND", "de", ""),),
        "DE-TH": (Entity("Thüringen", "DE-TH", "LAND", "de", ""),),
    }
