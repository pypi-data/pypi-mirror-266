"""ISO 3166-2 RW standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:RW
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "RW-01": (
            Entity("City of Kigali", "RW-01", "CITY", "en", ""),
            Entity("Umujyi wa Kigali", "RW-01", "CITY", "rw", ""),
            Entity("Ville de Kigali", "RW-01", "CITY", "fr", ""),
        ),
        "RW-02": (
            Entity("Eastern", "RW-02", "PROVINCE", "en", ""),
            Entity("Est", "RW-02", "PROVINCE", "fr", ""),
            Entity("Iburasirazuba", "RW-02", "PROVINCE", "rw", ""),
        ),
        "RW-03": (
            Entity("Amajyaruguru", "RW-03", "PROVINCE", "rw", ""),
            Entity("Nord", "RW-03", "PROVINCE", "fr", ""),
            Entity("Northern", "RW-03", "PROVINCE", "en", ""),
        ),
        "RW-04": (
            Entity("Iburengerazuba", "RW-04", "PROVINCE", "rw", ""),
            Entity("Ouest", "RW-04", "PROVINCE", "fr", ""),
            Entity("Western", "RW-04", "PROVINCE", "en", ""),
        ),
        "RW-05": (
            Entity("Amajyepfo", "RW-05", "PROVINCE", "rw", ""),
            Entity("Southern", "RW-05", "PROVINCE", "en", ""),
            Entity("Sud", "RW-05", "PROVINCE", "fr", ""),
        ),
    }
