"""ISO 3166-2 VU standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:VU
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "VU-MAP": (
            Entity("Malampa", "VU-MAP", "PROVINCE", "en", ""),
            Entity("Malampa", "VU-MAP", "PROVINCE", "fr", ""),
        ),
        "VU-PAM": (
            Entity("Pénama", "VU-PAM", "PROVINCE", "en", ""),
            Entity("Pénama", "VU-PAM", "PROVINCE", "fr", ""),
        ),
        "VU-SAM": (
            Entity("Sanma", "VU-SAM", "PROVINCE", "en", ""),
            Entity("Sanma", "VU-SAM", "PROVINCE", "fr", ""),
        ),
        "VU-SEE": (
            Entity("Shéfa", "VU-SEE", "PROVINCE", "en", ""),
            Entity("Shéfa", "VU-SEE", "PROVINCE", "fr", ""),
        ),
        "VU-TAE": (
            Entity("Taféa", "VU-TAE", "PROVINCE", "en", ""),
            Entity("Taféa", "VU-TAE", "PROVINCE", "fr", ""),
        ),
        "VU-TOB": (
            Entity("Torba", "VU-TOB", "PROVINCE", "en", ""),
            Entity("Torba", "VU-TOB", "PROVINCE", "fr", ""),
        ),
    }
