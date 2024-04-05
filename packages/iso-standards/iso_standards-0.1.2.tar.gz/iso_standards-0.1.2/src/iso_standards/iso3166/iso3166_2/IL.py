"""ISO 3166-2 IL standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:IL
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "IL-D": (
            Entity("Al Janūbī", "IL-D", "DISTRICT", "ar", ""),
            Entity("HaDarom", "IL-D", "DISTRICT", "he", ""),
        ),
        "IL-HA": (
            Entity("H̱efa", "IL-HA", "DISTRICT", "he", ""),
            Entity("Ḩayfā", "IL-HA", "DISTRICT", "ar", ""),
        ),
        "IL-JM": (
            Entity("Al Quds", "IL-JM", "DISTRICT", "ar", ""),
            Entity("Yerushalayim", "IL-JM", "DISTRICT", "he", ""),
        ),
        "IL-M": (
            Entity("Al Awsaţ", "IL-M", "DISTRICT", "ar", ""),
            Entity("HaMerkaz", "IL-M", "DISTRICT", "he", ""),
        ),
        "IL-TA": (
            Entity("Tall Abīb", "IL-TA", "DISTRICT", "ar", ""),
            Entity("Tel Aviv", "IL-TA", "DISTRICT", "he", ""),
        ),
        "IL-Z": (
            Entity("Ash Shamālī", "IL-Z", "DISTRICT", "ar", ""),
            Entity("HaTsafon", "IL-Z", "DISTRICT", "he", ""),
        ),
    }
