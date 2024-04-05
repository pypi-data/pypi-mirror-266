"""ISO 3166-2 SN standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SN
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SN-DB": (Entity("Diourbel", "SN-DB", "REGION", "fr", ""),),
        "SN-DK": (Entity("Dakar", "SN-DK", "REGION", "fr", ""),),
        "SN-FK": (Entity("Fatick", "SN-FK", "REGION", "fr", ""),),
        "SN-KA": (Entity("Kaffrine", "SN-KA", "REGION", "fr", ""),),
        "SN-KD": (Entity("Kolda", "SN-KD", "REGION", "fr", ""),),
        "SN-KE": (Entity("Kédougou", "SN-KE", "REGION", "fr", ""),),
        "SN-KL": (Entity("Kaolack", "SN-KL", "REGION", "fr", ""),),
        "SN-LG": (Entity("Louga", "SN-LG", "REGION", "fr", ""),),
        "SN-MT": (Entity("Matam", "SN-MT", "REGION", "fr", ""),),
        "SN-SE": (Entity("Sédhiou", "SN-SE", "REGION", "fr", ""),),
        "SN-SL": (Entity("Saint-Louis", "SN-SL", "REGION", "fr", ""),),
        "SN-TC": (Entity("Tambacounda", "SN-TC", "REGION", "fr", ""),),
        "SN-TH": (Entity("Thiès", "SN-TH", "REGION", "fr", ""),),
        "SN-ZG": (Entity("Ziguinchor", "SN-ZG", "REGION", "fr", ""),),
    }
