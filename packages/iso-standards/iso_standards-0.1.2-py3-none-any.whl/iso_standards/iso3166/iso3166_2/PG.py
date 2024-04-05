"""ISO 3166-2 PG standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:PG
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "PG-CPK": (Entity("Chimbu", "PG-CPK", "PROVINCE", "en", ""),),
        "PG-CPM": (Entity("Central", "PG-CPM", "PROVINCE", "en", ""),),
        "PG-EBR": (Entity("East New Britain", "PG-EBR", "PROVINCE", "en", ""),),
        "PG-EHG": (Entity("Eastern Highlands", "PG-EHG", "PROVINCE", "en", ""),),
        "PG-EPW": (Entity("Enga", "PG-EPW", "PROVINCE", "en", ""),),
        "PG-ESW": (Entity("East Sepik", "PG-ESW", "PROVINCE", "en", ""),),
        "PG-GPK": (Entity("Gulf", "PG-GPK", "PROVINCE", "en", ""),),
        "PG-HLA": (Entity("Hela", "PG-HLA", "PROVINCE", "en", ""),),
        "PG-JWK": (Entity("Jiwaka", "PG-JWK", "PROVINCE", "en", ""),),
        "PG-MBA": (Entity("Milne Bay", "PG-MBA", "PROVINCE", "en", ""),),
        "PG-MPL": (Entity("Morobe", "PG-MPL", "PROVINCE", "en", ""),),
        "PG-MPM": (Entity("Madang", "PG-MPM", "PROVINCE", "en", ""),),
        "PG-MRL": (Entity("Manus", "PG-MRL", "PROVINCE", "en", ""),),
        "PG-NCD": (Entity("National Capital District", "PG-NCD", "DISTRICT", "en", ""),),
        "PG-NIK": (Entity("New Ireland", "PG-NIK", "PROVINCE", "en", ""),),
        "PG-NPP": (Entity("Northern", "PG-NPP", "PROVINCE", "en", ""),),
        "PG-NSB": (Entity("Bougainville", "PG-NSB", "AUTONOMOUS REGION", "en", ""),),
        "PG-SAN": (Entity("West Sepik", "PG-SAN", "PROVINCE", "en", ""),),
        "PG-SHM": (Entity("Southern Highlands", "PG-SHM", "PROVINCE", "en", ""),),
        "PG-WBK": (Entity("West New Britain", "PG-WBK", "PROVINCE", "en", ""),),
        "PG-WHM": (Entity("Western Highlands", "PG-WHM", "PROVINCE", "en", ""),),
        "PG-WPD": (Entity("Western", "PG-WPD", "PROVINCE", "en", ""),),
    }
