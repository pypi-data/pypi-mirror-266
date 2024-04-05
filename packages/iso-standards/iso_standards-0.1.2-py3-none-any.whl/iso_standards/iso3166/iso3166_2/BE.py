"""ISO 3166-2 BE standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BE
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BE-BRU": (
            Entity("Brussels Hoofdstedelijk Gewest", "BE-BRU", "REGION", "nl", ""),
            Entity("Bruxelles-Capitale", "BE-BRU", "REGION", "fr", ""),
        ),
        "BE-VAN": (Entity("Antwerpen", "BE-VAN", "PROVINCE", "nl", "BE-VLG"),),
        "BE-VBR": (Entity("Vlaams-Brabant", "BE-VBR", "PROVINCE", "nl", "BE-VLG"),),
        "BE-VLG": (Entity("Vlaams Gewest", "BE-VLG", "REGION", "nl", ""),),
        "BE-VLI": (Entity("Limburg", "BE-VLI", "PROVINCE", "nl", "BE-VLG"),),
        "BE-VOV": (Entity("Oost-Vlaanderen", "BE-VOV", "PROVINCE", "nl", "BE-VLG"),),
        "BE-VWV": (Entity("West-Vlaanderen", "BE-VWV", "PROVINCE", "nl", "BE-VLG"),),
        "BE-WAL": (Entity("wallonne", "BE-WAL", "REGION", "fr", ""),),
        "BE-WBR": (Entity("Brabant wallon", "BE-WBR", "PROVINCE", "fr", "BE-WAL"),),
        "BE-WHT": (Entity("Hainaut", "BE-WHT", "PROVINCE", "fr", "BE-WAL"),),
        "BE-WLG": (Entity("Liège", "BE-WLG", "PROVINCE", "fr", "BE-WAL"),),
        "BE-WLX": (Entity("Luxembourg", "BE-WLX", "PROVINCE", "fr", "BE-WAL"),),
        "BE-WNA": (Entity("Namur", "BE-WNA", "PROVINCE", "fr", "BE-WAL"),),
    }
