"""ISO 3166-2 GQ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:GQ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "GQ-AN": (
            Entity("Annobon", "GQ-AN", "PROVINCE", "fr", "GQ-I"),
            Entity("Annobón", "GQ-AN", "PROVINCE", "es", "GQ-I"),
            Entity("Ano Bom", "GQ-AN", "PROVINCE", "pt", "GQ-I"),
        ),
        "GQ-BN": (
            Entity("Bioko Nord", "GQ-BN", "PROVINCE", "fr", "GQ-I"),
            Entity("Bioko Norte", "GQ-BN", "PROVINCE", "pt", "GQ-I"),
            Entity("Bioko Norte", "GQ-BN", "PROVINCE", "es", "GQ-I"),
        ),
        "GQ-BS": (
            Entity("Bioko Sud", "GQ-BS", "PROVINCE", "fr", "GQ-I"),
            Entity("Bioko Sul", "GQ-BS", "PROVINCE", "pt", "GQ-I"),
            Entity("Bioko Sur", "GQ-BS", "PROVINCE", "es", "GQ-I"),
        ),
        "GQ-C": (
            Entity("Região Continental", "GQ-C", "REGION", "pt", ""),
            Entity("Región Continental", "GQ-C", "REGION", "es", ""),
            Entity("Région Continentale", "GQ-C", "REGION", "fr", ""),
        ),
        "GQ-CS": (
            Entity("Centro Sud", "GQ-CS", "PROVINCE", "fr", "GQ-C"),
            Entity("Centro Sul", "GQ-CS", "PROVINCE", "pt", "GQ-C"),
            Entity("Centro Sur", "GQ-CS", "PROVINCE", "es", "GQ-C"),
        ),
        "GQ-DJ": (
            Entity("Djibloho", "GQ-DJ", "PROVINCE", "fr", "GQ-C"),
            Entity("Djibloho", "GQ-DJ", "PROVINCE", "pt", "GQ-C"),
            Entity("Djibloho", "GQ-DJ", "PROVINCE", "es", "GQ-C"),
        ),
        "GQ-I": (
            Entity("Região Insular", "GQ-I", "REGION", "pt", ""),
            Entity("Región Insular", "GQ-I", "REGION", "es", ""),
            Entity("Région Insulaire", "GQ-I", "REGION", "fr", ""),
        ),
        "GQ-KN": (
            Entity("Kié-Ntem", "GQ-KN", "PROVINCE", "fr", "GQ-C"),
            Entity("Kié-Ntem", "GQ-KN", "PROVINCE", "pt", "GQ-C"),
            Entity("Kié-Ntem", "GQ-KN", "PROVINCE", "es", "GQ-C"),
        ),
        "GQ-LI": (
            Entity("Litoral", "GQ-LI", "PROVINCE", "pt", "GQ-C"),
            Entity("Litoral", "GQ-LI", "PROVINCE", "es", "GQ-C"),
            Entity("Littoral", "GQ-LI", "PROVINCE", "fr", "GQ-C"),
        ),
        "GQ-WN": (
            Entity("Wele-Nzas", "GQ-WN", "PROVINCE", "fr", "GQ-C"),
            Entity("Wele-Nzas", "GQ-WN", "PROVINCE", "pt", "GQ-C"),
            Entity("Wele-Nzas", "GQ-WN", "PROVINCE", "es", "GQ-C"),
        ),
    }
