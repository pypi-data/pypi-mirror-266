"""ISO 3166-2 CI standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CI
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CI-AB": (Entity("Abidjan", "CI-AB", "AUTONOMOUS DISTRICT", "fr", ""),),
        "CI-BS": (Entity("Bas-Sassandra", "CI-BS", "DISTRICT", "fr", ""),),
        "CI-CM": (Entity("Comoé", "CI-CM", "DISTRICT", "fr", ""),),
        "CI-DN": (Entity("Denguélé", "CI-DN", "DISTRICT", "fr", ""),),
        "CI-GD": (Entity("Gôh-Djiboua", "CI-GD", "DISTRICT", "fr", ""),),
        "CI-LC": (Entity("Lacs", "CI-LC", "DISTRICT", "fr", ""),),
        "CI-LG": (Entity("Lagunes", "CI-LG", "DISTRICT", "fr", ""),),
        "CI-MG": (Entity("Montagnes", "CI-MG", "DISTRICT", "fr", ""),),
        "CI-SM": (Entity("Sassandra-Marahoué", "CI-SM", "DISTRICT", "fr", ""),),
        "CI-SV": (Entity("Savanes", "CI-SV", "DISTRICT", "fr", ""),),
        "CI-VB": (Entity("Vallée du Bandama", "CI-VB", "DISTRICT", "fr", ""),),
        "CI-WR": (Entity("Woroba", "CI-WR", "DISTRICT", "fr", ""),),
        "CI-YM": (Entity("Yamoussoukro", "CI-YM", "AUTONOMOUS DISTRICT", "fr", ""),),
        "CI-ZZ": (Entity("Zanzan", "CI-ZZ", "DISTRICT", "fr", ""),),
    }
