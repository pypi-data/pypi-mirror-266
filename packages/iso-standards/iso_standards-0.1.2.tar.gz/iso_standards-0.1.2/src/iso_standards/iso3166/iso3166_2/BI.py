"""ISO 3166-2 BI standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BI
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BI-BB": (
            Entity("Bubanza", "BI-BB", "PROVINCE", "fr", ""),
            Entity("Bubanza", "BI-BB", "PROVINCE", "rn", ""),
        ),
        "BI-BL": (
            Entity("Bujumbura Rural", "BI-BL", "PROVINCE", "fr", ""),
            Entity("Bujumbura Rural", "BI-BL", "PROVINCE", "rn", ""),
        ),
        "BI-BM": (
            Entity("Bujumbura Mairie", "BI-BM", "PROVINCE", "fr", ""),
            Entity("Bujumbura Mairie", "BI-BM", "PROVINCE", "rn", ""),
        ),
        "BI-BR": (
            Entity("Bururi", "BI-BR", "PROVINCE", "fr", ""),
            Entity("Bururi", "BI-BR", "PROVINCE", "rn", ""),
        ),
        "BI-CA": (
            Entity("Cankuzo", "BI-CA", "PROVINCE", "fr", ""),
            Entity("Cankuzo", "BI-CA", "PROVINCE", "rn", ""),
        ),
        "BI-CI": (
            Entity("Cibitoke", "BI-CI", "PROVINCE", "fr", ""),
            Entity("Cibitoke", "BI-CI", "PROVINCE", "rn", ""),
        ),
        "BI-GI": (
            Entity("Gitega", "BI-GI", "PROVINCE", "fr", ""),
            Entity("Gitega", "BI-GI", "PROVINCE", "rn", ""),
        ),
        "BI-KI": (
            Entity("Kirundo", "BI-KI", "PROVINCE", "fr", ""),
            Entity("Kirundo", "BI-KI", "PROVINCE", "rn", ""),
        ),
        "BI-KR": (
            Entity("Karuzi", "BI-KR", "PROVINCE", "fr", ""),
            Entity("Karuzi", "BI-KR", "PROVINCE", "rn", ""),
        ),
        "BI-KY": (
            Entity("Kayanza", "BI-KY", "PROVINCE", "fr", ""),
            Entity("Kayanza", "BI-KY", "PROVINCE", "rn", ""),
        ),
        "BI-MA": (
            Entity("Makamba", "BI-MA", "PROVINCE", "fr", ""),
            Entity("Makamba", "BI-MA", "PROVINCE", "rn", ""),
        ),
        "BI-MU": (
            Entity("Muramvya", "BI-MU", "PROVINCE", "fr", ""),
            Entity("Muramvya", "BI-MU", "PROVINCE", "rn", ""),
        ),
        "BI-MW": (
            Entity("Mwaro", "BI-MW", "PROVINCE", "fr", ""),
            Entity("Mwaro", "BI-MW", "PROVINCE", "rn", ""),
        ),
        "BI-MY": (
            Entity("Muyinga", "BI-MY", "PROVINCE", "fr", ""),
            Entity("Muyinga", "BI-MY", "PROVINCE", "rn", ""),
        ),
        "BI-NG": (
            Entity("Ngozi", "BI-NG", "PROVINCE", "fr", ""),
            Entity("Ngozi", "BI-NG", "PROVINCE", "rn", ""),
        ),
        "BI-RM": (
            Entity("Rumonge", "BI-RM", "PROVINCE", "fr", ""),
            Entity("Rumonge", "BI-RM", "PROVINCE", "rn", ""),
        ),
        "BI-RT": (
            Entity("Rutana", "BI-RT", "PROVINCE", "fr", ""),
            Entity("Rutana", "BI-RT", "PROVINCE", "rn", ""),
        ),
        "BI-RY": (
            Entity("Ruyigi", "BI-RY", "PROVINCE", "fr", ""),
            Entity("Ruyigi", "BI-RY", "PROVINCE", "rn", ""),
        ),
    }
