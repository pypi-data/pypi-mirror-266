"""ISO 3166-2 DJ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:DJ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "DJ-AR": (
            Entity("Arta", "DJ-AR", "REGION", "fr", ""),
            Entity("‘Artā", "DJ-AR", "REGION", "ar", ""),
        ),
        "DJ-AS": (
            Entity("Ali Sabieh", "DJ-AS", "REGION", "fr", ""),
            Entity("‘Alī Şabīḩ", "DJ-AS", "REGION", "ar", ""),
        ),
        "DJ-DI": (
            Entity("Dikhil", "DJ-DI", "REGION", "fr", ""),
            Entity("Dikhīl", "DJ-DI", "REGION", "ar", ""),
        ),
        "DJ-DJ": (
            Entity("Djibouti", "DJ-DJ", "CITY", "fr", ""),
            Entity("Jībūtī", "DJ-DJ", "CITY", "ar", ""),
        ),
        "DJ-OB": (
            Entity("Awbūk", "DJ-OB", "REGION", "ar", ""),
            Entity("Obock", "DJ-OB", "REGION", "fr", ""),
        ),
        "DJ-TA": (
            Entity("Tadjourah", "DJ-TA", "REGION", "fr", ""),
            Entity("Tājūrah", "DJ-TA", "REGION", "ar", ""),
        ),
    }
