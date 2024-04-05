"""ISO 3166-2 GW standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:GW
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "GW-BA": (Entity("Bafatá", "GW-BA", "REGION", "pt", "GW-L"),),
        "GW-BL": (Entity("Bolama / Bijagós", "GW-BL", "REGION", "pt", "GW-S"),),
        "GW-BM": (Entity("Biombo", "GW-BM", "REGION", "pt", "GW-N"),),
        "GW-BS": (Entity("Bissau", "GW-BS", "AUTONOMOUS SECTOR", "pt", ""),),
        "GW-CA": (Entity("Cacheu", "GW-CA", "REGION", "pt", "GW-N"),),
        "GW-GA": (Entity("Gabú", "GW-GA", "REGION", "pt", "GW-L"),),
        "GW-L": (Entity("Leste", "GW-L", "PROVINCE", "pt", ""),),
        "GW-N": (Entity("Norte", "GW-N", "PROVINCE", "pt", ""),),
        "GW-OI": (Entity("Oio", "GW-OI", "REGION", "pt", "GW-N"),),
        "GW-QU": (Entity("Quinara", "GW-QU", "REGION", "pt", "GW-S"),),
        "GW-S": (Entity("Sul", "GW-S", "PROVINCE", "pt", ""),),
        "GW-TO": (Entity("Tombali", "GW-TO", "REGION", "pt", "GW-S"),),
    }
