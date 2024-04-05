"""ISO 3166-2 GH standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:GH
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "GH-AA": (Entity("Greater Accra", "GH-AA", "REGION", "en", ""),),
        "GH-AF": (Entity("Ahafo", "GH-AF", "REGION", "en", ""),),
        "GH-AH": (Entity("Ashanti", "GH-AH", "REGION", "en", ""),),
        "GH-BE": (Entity("Bono East", "GH-BE", "REGION", "en", ""),),
        "GH-BO": (Entity("Bono", "GH-BO", "REGION", "en", ""),),
        "GH-CP": (Entity("Central", "GH-CP", "REGION", "en", ""),),
        "GH-EP": (Entity("Eastern", "GH-EP", "REGION", "en", ""),),
        "GH-NE": (Entity("North East", "GH-NE", "REGION", "en", ""),),
        "GH-NP": (Entity("Northern", "GH-NP", "REGION", "en", ""),),
        "GH-OT": (Entity("Oti", "GH-OT", "REGION", "en", ""),),
        "GH-SV": (Entity("Savannah", "GH-SV", "REGION", "en", ""),),
        "GH-TV": (Entity("Volta", "GH-TV", "REGION", "en", ""),),
        "GH-UE": (Entity("Upper East", "GH-UE", "REGION", "en", ""),),
        "GH-UW": (Entity("Upper West", "GH-UW", "REGION", "en", ""),),
        "GH-WN": (Entity("Western North", "GH-WN", "REGION", "en", ""),),
        "GH-WP": (Entity("Western", "GH-WP", "REGION", "en", ""),),
    }
